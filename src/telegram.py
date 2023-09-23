# from operator import truediv
from telebot import types
import requests
import json
import datetime
import re
import time
import random
import os
import traceback
import sqlite3 as sql
from src.helpers import get_info, open_dialogue, update_clients, db_find_value, delete_client, log_report, new_client, \
    info_soon_check, client_info_msg, close_dialogue, bot, vk, fb_bot, autopay, get_tariffs, close_all_dialogues, \
    select_all_exch
from trial_period import message_trial_period_first, trial_period_offer, message_trial_period_ok, \
    message_trial_period_err, message_trial_period_cancel, add_trial_check, message_trial_period_button, add_trial_tg

# import gspread
from src.change_language import get_user_lang, frases_dict, set_user_lang
from src import currency_change_queries, curr_text, messages, currency_helpers, helpers, config

# Temp data for mailing and DB editing commands
temp = {"tariffs": [], "mail_text": "", "wrong_email": "", "true_email": ""}
curr_temp = {}


# --------------------------------------------------
def tg_to_tg(to_id, message, from_support=False, review=False, curr_change=False):
    """ Transfers messages from client to support and back
        Used instead of TG API forward_message method to be able to reply every client,
        even those who restricted forwarding """

    text = message.text or message.caption or ''

    # Add info about client to message
    if not from_support:

        # Upper part of the message with emoji and name
        header = f"\U0001F4E2 Отзыв\n" if review \
            else f"\U0001F4AC{message.from_user.first_name} {message.from_user.last_name}\n"

        # Bottom part of the message with id and social network name, so we can reply back
        check = "\U00002705" if get_info(
            "verified", "tg_id", message.chat.id) else ''
        bottom = f"{message.chat.id} Telegram{check}"
        text = header + text + "\n\n"
        # Add client tariff info
        if not info_soon_check(message.chat.id, 'tg_id'):
            text += "\n" + client_info_msg("tg_id", message.chat.id, curr_change)
        text += bottom

    if message.text:
        bot.send_message(to_id, text)
    if message.photo:
        photo_max_res = sorted(
            message.photo, key=lambda x: x.height)[-1].file_id
        bot.send_photo(to_id, photo_max_res, caption=text)
    if message.video:
        bot.send_video(to_id, message.video.file_id, caption=text)
    if message.document:
        bot.send_document(to_id, message.document.file_id, caption=text)
    if message.voice:
        bot.send_voice(to_id, message.voice.file_id)
        # Voice message has no caption, so send empty text message with top+bottom borders to be able to reply
        # Same for audio and stickers
        if not from_support:
            bot.send_message(to_id, text)

    if message.audio:
        bot.send_audio(to_id, message.audio.file_id)
        if not from_support:
            bot.send_message(to_id, text)

    if message.sticker:
        bot.send_sticker(to_id, message.sticker.file_id)
        if not from_support:
            bot.send_message(to_id, text)


# --------------------------------------------------
def copy_send_message(to_chat_id, from_chat_id, message_id):
    """ Copy and send telegram message """

    url = f'https://api.telegram.org/bot{config.tg_token}/copyMessage'
    requests.post(url, json={"chat_id": f"{to_chat_id}", "from_chat_id": f"{from_chat_id}",
                             "message_id": f"{message_id}"})


# --------------------------------------------------
def tg_to_vk(message, to_id):
    """ Send message with attachments to VK """

    if message.text:
        vk.messages.send(user_id=int(to_id), random_id=random.randint(
            0, 2147483646), message=message.text)
    elif message.photo:
        photo_tg_to_vk(to_id, save_file(message), message.caption)
    elif message.document:
        doc_tg_to_vk(to_id, save_file(message), message.caption)


# -------------------------------------------------
def tg_to_fb(message, to_id):
    """ Send text message to FB """

    if message.text:
        fb_bot.send_text_message(to_id, message.text)


# -------------------------------------------------
def photo_tg_to_vk(user_id, path, message):
    """ Upload photo to VK servers and send message """

    server = vk.photos.getMessagesUploadServer()
    upload = requests.post(server['upload_url'], files={
        'photo': open(path, 'rb')}).json()
    save = vk.photos.saveMessagesPhoto(
        photo=upload['photo'], server=upload['server'], hash=upload['hash'])[0]
    att = f"photo{save['owner_id']}_{save['id']}"
    vk.messages.send(user_id=int(user_id), random_id=random.randint(1, 2147483647), message=message,
                     attachment=att)


# -------------------------------------------------
def doc_tg_to_vk(user_id, path, message):
    """ Upload document to VK servers and send message """

    server = vk.docs.getMessagesUploadServer(peer_id=user_id, type="doc")
    upload = requests.post(server['upload_url'], files={
        'file': open(path, 'rb')}).json()
    save = vk.docs.save(file=upload['file'])
    att = f"doc{save['doc']['owner_id']}_{save['doc']['id']}"
    vk.messages.send(user_id=user_id, random_id=random.randint(
        1, 2147483647), message=message, attachment=att)


# -------------------------------------------------
def save_file(message, folder=config.files_path, check=False):
    """ Save attachment from message to local folder and return its path """
    path = ""
    if message.photo:
        file_id = message.photo[-1].file_id
        file_name = bot.get_file_url(file_id).split('/')[-1]
        a = bot.get_file(file_id)
        downloaded_file = bot.download_file(a.file_path)
        path = os.path.join(folder, file_name)

        if check and file_name in os.listdir(config.pay_imgs_path):
            return "File already in folder"

        with open(path, "wb") as new_file:
            new_file.write(downloaded_file)

    elif message.document:
        name = message.document.file_name
        a = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(a.file_path)
        path = folder + name
        with open(path, "wb") as new_file:
            new_file.write(downloaded_file)

    return path


# --------------------------------------------------
def spam(tariffs_list, text, sender, vk_only=False, tg_only=False):
    """ Send message to every known messenger for every client with chosen tariffs """

    with sql.connect(config.db_file) as con:
        clients_list = []

        # Get IDs of every client with chosen tariffs
        for t in tariffs_list:
            cur = con.cursor()
            cur.execute(
                "SELECT tg_id, vk_id, fb_id FROM clients WHERE tariff = ?", (t,))
            clients_list += cur.fetchall()

    for client in clients_list:
        try:
            sent = False
            tg_id, vk_id, fb_id = client[:3]
            if not vk_only and tg_id and tg_id != "0":
                copy_send_message(tg_id, sender, temp['message_id'])
                sent = True
            if not tg_only and vk_id and vk_id != "0":
                vk.messages.send(user_id=int(vk_id), random_id=random.randint(
                    0, 2147483646), message=text)
                sent = True
            # elif fb_id != "0":
            # fb_bot.send_text_message(fb_id, text)  # Temporarily off

            # Delay to prevent api errors
            if sent:
                pass
        except Exception as e:
            print(f'Failed spamming to client {client}.\nException:\n', e)


# --------------------------------------------------
def check_mail_edit(message, command='/почта'):
    """ Check if message fits options for DB editing commands """

    # Check if message is sent by bot owner
    user_check = message.from_user.id in [config.my_id, config.owner_id]

    if user_check and message.text == command:
        return True

    # Every message except starting ('/почта') must be reply to bot message
    if not message.reply_to_message or not message.reply_to_message.text:
        return False

    reply_text = message.reply_to_message.text

    # Check if reply message sender is bot
    bot_check = message.reply_to_message.from_user.id == config.bot_id

    # Check if reply message text is special text that bot sends to owner
    text_check = ""
    if command == '/почта':
        text_check = reply_text in [
            messages.edit_wrong_mail, messages.edit_true_mail, messages.edit_confirm]
    elif command == '/изменить':
        text_check = reply_text in [
            messages.edit_by_mail_msg, messages.edit_format_error]

    return user_check and bot_check and text_check


# --------------------------------------------------
def check_mailing(message):
    """ Check if message fits options for mailing commands """

    # Check if message is sent by bot owner
    user_check = message.from_user.id in [config.my_id, config.owner_id]
    txt = message.text or message.caption

    if user_check and txt == "/рассылка":
        return True

    # Every message except starting ('/рассылка') must be reply to bot message
    if not message.reply_to_message or not message.reply_to_message.text:
        return False

    reply_text = message.reply_to_message.text
    # Check if reply message sender is bot
    bot_check = message.reply_to_message.from_user.id == config.bot_id

    # Check if reply message text is special text that bot sends to owner
    text_check = reply_text in [messages.mailing_tariffs, messages.mailing_message] or \
                 reply_text.startswith("Следующие тарифы:")

    return user_check and bot_check and text_check


# --------------------------------------------------
def support(message, urgent=False):
    """ Handles every attempt to open support dialogue. Does not open if not urgent and not in working time """
    lang = get_user_lang(message.chat.id)

    buttons = types.InlineKeyboardMarkup()

    # User trying to contact support in non working time
    # if False and not urgent:
    # if not 17 <= datetime.datetime.today().hour < 22 or datetime.datetime.today().isoweekday() in [6, 7]:
    # buttons.add(types.InlineKeyboardButton(
    # text=frases_dict["srochno"][lang], callback_data="urgent"))
    # bot.send_message(
    # message.chat.id, messages.non_working[lang], reply_markup=buttons)
    # return

    open_dialogue("tg_id", message.chat.id)
    buttons = types.InlineKeyboardMarkup()

    buttons.add(types.InlineKeyboardButton(
        text=frases_dict["init_setup"][lang], callback_data="install"))
    buttons.add(types.InlineKeyboardButton(
        text=frases_dict["btn_other"][lang], callback_data="other"))
    buttons.add(types.InlineKeyboardButton(
        text="ZGC SHOP", callback_data="market"))

    # Ask user to choose problem type
    msg = messages.type_support[lang]
    print("type_support ok, lang=", lang)
    user_info = db_find_value("tg_id", message.chat.id)
    sub = user_info['sub']

    if sub != '-' and int(user_info['verified']):
        msg += frases_dict["your_sub"][lang] + sub

    bot.send_message(message.chat.id, msg, reply_markup=buttons)


# --------------------------------------------------
def initial_buttons(message, send_text=""):
    """ Send user message with default reply keyboard"""
    lang = get_user_lang(message.from_user.id)
    if send_text == "":
        send_text = messages.buttons_menu[lang]
    markup_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_pay = types.InlineKeyboardButton(frases_dict["payment"][lang])
    item_shop = types.InlineKeyboardButton("\U0001F6D2 ZGC SHOP")
    item_trial = types.InlineKeyboardButton(frases_dict["trial"][lang])
    item_promo = types.InlineKeyboardButton(frases_dict["knowmore"][lang])
    markup_buttons.add(item_pay, item_trial, item_promo)

    item_coop = types.InlineKeyboardButton(frases_dict["coop"][lang])
    item_connection = types.InlineKeyboardButton(frases_dict["contact"][lang])
    change_lang = types.InlineKeyboardButton("Change language")
    if lang == "ru":
        item_change = types.InlineKeyboardButton("\U0001F4B1 Обмен валют")
        markup_buttons.add(item_shop, item_coop, change_lang, item_change, item_connection)
    else:
        markup_buttons.add(item_shop, item_coop, change_lang, item_connection)

    bot.send_message(message.chat.id, send_text, reply_markup=markup_buttons)


@bot.message_handler(func=lambda message: message.chat.id == config.my_id and
                                          message.text[:8] == "test_sql")
def zakharov_testing(message):
    a = currency_change_queries.alter_table(message.text)
    bot.send_message(message.chat.id, a)


@bot.message_handler(func=lambda message: message.chat.id == 197898957000)
def cow(message):
    """ Korova """

    bot.send_audio(
        message.chat.id, "CQACAgIAAxkBAALKP1-5Lbsw_SWny8UT3NIbArp_mlZcAAJPCAACqgABwUl8U_s6W_nHxB4E")


@bot.message_handler(commands=["start"])
def start(message):
    """ Ask user to send his email address if not identified. Otherwise send default message with reply keyboard """

    if not db_find_value("tg_id", message.chat.id):
        bot.send_message(message.chat.id, messages.send_email['ru'])
    else:
        initial_buttons(message)


@bot.message_handler(func=lambda message: message.chat.id != config.group_id and
                                          message.chat.id != config.exchange_id and
                                          not db_find_value("tg_id", message.chat.id),
                     content_types=['text', 'photo', 'video', 'voice', 'audio', 'sticker', 'document'])
def unknown_user(message):
    """ Handle all messages if user is not identified """
    # lang = get_user_lang(message.from_user.id)

    # Check if message text has '@' between some non-space symbols
    if not message.text or not re.findall(r"\S+@\S+", message.text):
        bot.send_message(message.chat.id, messages.send_email["ru"])
        return

    email = re.findall(r"\S+@\S+", message.text)[0].lower()
    # Suppose user entered email, look for it in database
    email_info = db_find_value("email", email)

    # Email not found, insert new row in DB with that email and user ID
    if not email_info:
        new_client(email, "tg_id", message.chat.id)
        trial_period_offer(message, message_trial_period_first["ru"])

    # Email is already used by user with other ID, ask to immediately contact us
    elif email_info['tg_id'] != "0":
        new_client("-", "tg_id", message.chat.id)
        open_dialogue("tg_id", message.chat.id)
        initial_buttons(message, messages.email_already_used["ru"])

    # Email found in DB and not used by other ID, update DB
    else:
        update_clients(["email", email], ["tg_id", message.chat.id])
        initial_buttons(message)


@bot.message_handler(
    func=lambda message: message.chat.id in [config.my_id, config.owner_id] and message.text.split()[0] == '/wechat')
def get_wechat(message):
    client_id = message.text.split()[1]
    wc = currency_change_queries.check_user(tg_id=client_id)
    bot.send_message(message.from_user.id, f'Вичат пользователя {client_id} - {wc}')


@bot.message_handler(func=lambda message: message.text == "Change language")
def change_language(message):
    set_user_lang(message.from_user.id)
    initial_buttons(message)


@bot.message_handler(func=lambda message: message.text in list(frases_dict["contact"].values()))
def sup(message):
    """ Handles support button """
    support(message)


@bot.message_handler(func=lambda message: message.text in list(frases_dict["payment"].values()))
def pay(message):
    """ Handles payment button """
    lang = get_user_lang(message.from_user.id)
    open_dialogue("tg_id", message.chat.id, state="PAY")

    buttons = types.InlineKeyboardMarkup()
    buttons.add(types.InlineKeyboardButton(
        text=frases_dict["rub-gri"][lang], callback_data="rub"))
    buttons.add(types.InlineKeyboardButton(
        text=frases_dict["uan"][lang], callback_data="yuan"))
    buttons.add(types.InlineKeyboardButton(
        text=frases_dict["contact"][lang], callback_data="sup"))
    bot.send_message(
        message.chat.id, messages.pay_type[lang], reply_markup=buttons)


@bot.message_handler(func=lambda message: message.text in list(frases_dict["trial"].values()))
def trial(message):
    """ Handles free trial button """
    lang = get_user_lang(message.from_user.id)

    email = db_find_value("tg_id", message.chat.id)["email"]
    if not add_trial_check(email):
        bot.send_message(message.chat.id, message_trial_period_err[lang])
        initial_buttons(message)
    else:
        trial_period_offer(message, message_trial_period_button[lang])


@bot.message_handler(func=lambda message: message.text in list(frases_dict["knowmore"].values()))
def blog(message):
    """ Handles blog button """
    lang = get_user_lang(message.from_user.id)

    buttons = types.InlineKeyboardMarkup()
    buttons.add(types.InlineKeyboardButton(
        text=frases_dict["blog"][lang], url='https://market.zgc.su/zgcvpnblog'))
    bot.send_message(
        message.chat.id, frases_dict["blog_text"][lang], reply_markup=buttons)


# Обмен валют работает по своей собственной логике.
# Когда клиент выбирает "Обмен валют", создается элемент словаря с ключом id, и значением нового словаря.
# Далее он заполняет поля, после заполнения меняется state - поле во внутреннем словаре.
# И в зависимости от state выбираентся функция, которая сработает следующей.
@bot.message_handler(func=lambda message: message.text == "\U0001F4B1 Обмен валют")
def currency_change(message):
    user_wc = currency_change_queries.check_user(tg_id=message.chat.id)
    if not user_wc:
        bot.send_message(message.chat.id, curr_text.text_registration)
        curr_temp[message.chat.id] = {"state": "reg"}
    else:
        bot.send_message(message.chat.id, curr_text.yuan_0())
        bot.send_message(message.chat.id, curr_text.text_first_msg,
                         reply_markup=curr_text.text_first_msg_btns())
        curr_temp[message.chat.id] = {"state": "type"}
        curr_temp[message.chat.id]["wechat_id"] = user_wc


@bot.message_handler(func=lambda message: message.text == "\U0001F6AB Отменить обмен")
def cancel_exchange(message):
    text = curr_text.get_support_msg(message, curr_temp.get(message.chat.id, {}), True)
    helpers.send_msg_to_tg_exch(text, curr_temp.get(message.chat.id, {}).get("image", ''))
    helpers.open_dialogue_exch(message)
    bot.send_message(message.chat.id, "Заявка отменена!")
    if curr_temp.get(message.chat.id, None):
        del curr_temp[message.chat.id]
    initial_buttons(message)


@bot.message_handler(func=lambda message: curr_temp.get(message.chat.id, {}).get("state", None) == "reg")
def currency_reg(message):
    text = message.text  # currency_helpers.check_phone_number(message.text)
    if text:
        bot.send_message(message.chat.id, curr_text.yuan_0())
        currency_change_queries.add_user(text, message.chat.id)
        curr_temp[message.chat.id] = {"state": "type"}
        curr_temp[message.chat.id]["wechat_id"] = text
        bot.send_message(message.chat.id, curr_text.text_first_msg,
                         reply_markup=curr_text.text_first_msg_btns())
    else:
        bot.send_message(message.chat.id, curr_text.text_reg_error)


@bot.message_handler(func=lambda message: curr_temp.get(message.chat.id, {}).get("state", None) == "other")
def currency_other(message):
    curr_temp[message.chat.id]["dop_info"] = message.text
    msg_out = curr_text.get_support_msg(message, curr_temp[message.chat.id])
    helpers.send_msg_to_tg_exch(msg_out)
    # bot.send_message(message.chat.id)
    initial_buttons(message, curr_text.change_currency_final)
    helpers.open_dialogue("tg_id", message.chat.id, state="CURR")
    if curr_temp[message.chat.id]:
        del curr_temp[message.chat.id]


@bot.message_handler(func=lambda message:
curr_temp.get(message.chat.id, {}).get("state", None) == "count")
def currency_count(message):
    text = message.text.strip()
    if text.isdigit():
        curr_temp[message.chat.id]["count"] = text
        curr_temp[message.chat.id]['state'] = 'currency'
        if curr_temp[message.chat.id]["type"] == "покупка":
            exc = currency_helpers.get_rate('buy', int(text))
            curr_temp[message.chat.id]["exc"] = exc
            bot.send_message(message.chat.id, f"Курс для вас: {exc} рублей за юань")
            bot.send_message(message.chat.id, curr_text.buy_yuan_2, reply_markup=curr_text.curr_choice_btns())
        elif curr_temp[message.chat.id]["type"] == "продажа":
            exc = currency_helpers.get_rate('sell', int(text))
            curr_temp[message.chat.id]["exc"] = exc
            bot.send_message(message.chat.id, f"Курс для вас: {exc} рублей за юань")
            bot.send_message(message.chat.id, curr_text.sell_yuan_2, reply_markup=curr_text.curr_choice_btns())
    else:
        bot.send_message(message.chat.id, "Пожалуйста, введите только сумму, без лишних символов.")


@bot.message_handler(func=lambda message:
curr_temp.get(message.chat.id, {}).get("state", None) == "requisites",
                     content_types=['text', 'photo', 'video', 'voice', 'audio', 'sticker', 'document'])
def curr_final(message):
    if message.photo:
        curr_temp[message.chat.id]["image"] = message.photo[0].file_id
        curr_temp[message.chat.id]["requisites"] = message.caption if message.caption else "в изображении"
    if message.text:
        curr_temp[message.chat.id]["requisites"] = message.text
    t = curr_text.get_final_message(curr_temp[message.chat.id])
    bot.send_message(message.chat.id, t, reply_markup=curr_text.cancel_btn(final=True))
    curr_temp[message.chat.id]['state'] = 'final'


@bot.message_handler(func=lambda message:
curr_temp.get(message.chat.id, {}).get("state", None) == "final")
def curr_confirm(message):
    if message.text == "\u2705 Отправить заявку":
        text = curr_text.get_support_msg(message, curr_temp.get(message.chat.id, {}))
        helpers.send_msg_to_tg_exch(text, curr_temp.get(message.chat.id, {}).get("image", ''))

        del curr_temp[message.chat.id]
        bot.send_message(message.chat.id, curr_text.change_currency_final)
        initial_buttons(message)
        helpers.open_dialogue_exch(message)
    else:
        curr_temp[message.chat.id]["dop_info"] = curr_temp[message.chat.id].get('dop_info', '') + "\n" + message.text


@bot.message_handler(func=lambda message: message.text in list(frases_dict["forturk"].values()))
def tm(message):
    """ Handles for Turkmenistan button """
    lang = get_user_lang(message.from_user.id)
    buttons = types.InlineKeyboardMarkup()
    buttons.add(types.InlineKeyboardButton(
        text=frases_dict["tm_site"][lang], url='tm.zgc.su'))
    buttons.add(types.InlineKeyboardButton(text=frases_dict["tm_how"][lang],
                                           url='https://sites.google.com/view/zgcvpn/try?authuser=0'))
    bot.send_message(
        message.chat.id, messages.turk[lang], reply_markup=buttons)


@bot.message_handler(func=lambda message: message.text in list(frases_dict["coop"].values()))
def coop(message):
    """ Handles cooperation button """
    lang = get_user_lang(message.from_user.id)
    buttons = types.InlineKeyboardMarkup()
    buttons.add(types.InlineKeyboardButton(
        text=frases_dict["go_coop"][lang], url='https://zgcvpn.ru/partnership'))
    bot.send_message(
        message.chat.id, messages.coop[lang], reply_markup=buttons)


@bot.message_handler(func=lambda message: message.text == "\U0001F6D2 ZGC SHOP")
def shop(message):
    """ Handles zgc shop button """
    lang = get_user_lang(message.from_user.id)

    buttons = types.InlineKeyboardMarkup()
    buttons.add(types.InlineKeyboardButton(
        text="\U0001F6D2 ZGC SHOP", url='https://market.zgc.su'))
    buttons.add(types.InlineKeyboardButton(
        text=frases_dict["contact"][lang], callback_data='market'))
    bot.send_message(
        message.chat.id, messages.shop[lang], reply_markup=buttons)


@bot.callback_query_handler(func=lambda call: True)
def react(call):
    """ Handles all callback buttons """
    lang = get_user_lang(call.message.chat.id)

    buttons = types.InlineKeyboardMarkup()
    user_info = db_find_value('tg_id', call.message.chat.id)

    if call.data == "rub":
        phot = open('2023-05-04 12.27.06.jpg', 'rb')
        tariff_id = user_info['tariff']
        msg = messages.rub_text[lang]

        # If user has active tariff, send button allowing to extend his current tariff
        # Temporarily off
        if False and tariff_id in ['1', '2', '3', '22', '23']:
            buttons.add(types.InlineKeyboardButton(
                text="Продлить текущий тариф", callback_data=f"Р-{tariff_id}"))
            msg += f"\n\nВаш текущий тариф: {tariff_id}"
            bot.send_message(call.message.chat.id, msg,
                             parse_mode='Markdown', reply_markup=buttons)
        else:
            bot.send_message(call.message.chat.id, msg, parse_mode='Markdown')
        bot.send_photo(call.message.chat.id, phot, caption='Пример скриншота')

    elif call.data == "yuan":
        phot = open('2023-05-04 12.27.13.jpg', 'rb')
        bot.send_message(call.message.chat.id,
                         messages.yuan_text[lang], parse_mode='Markdown')
        bot.send_photo(call.message.chat.id, phot, caption='Пример скриншота')
    elif call.data == "install":
        bot.send_message(call.message.chat.id, messages.first_install[lang])
    elif call.data == "other":
        bot.send_message(call.message.chat.id,
                         messages.support[lang], parse_mode='Markdown')
    elif call.data == "market":
        open_dialogue("tg_id", call.message.chat.id)
        bot.send_message(call.message.chat.id,
                         frases_dict["hello_product"][lang])
    elif call.data == "urgent":
        support(call.message, urgent=True)
    elif call.data == "sup":
        support(call.message)

    # If user rated quality less than 5 and pushed feedback button, open dialogue for one message only
    elif call.data == "get_better":
        update_clients(["tg_id", call.message.chat.id],
                       ["state", "ONE MESSAGE"], ["review_time", f"{int(time.time())}"])
        bot.send_message(call.message.chat.id, messages.get_better[lang])

    elif call.data == "pay":
        buttons.add(types.InlineKeyboardButton(
            text=frases_dict["rub-gri"][lang], callback_data="rub"))
        buttons.add(types.InlineKeyboardButton(
            text=frases_dict["uan"][lang], callback_data="yuan"))
        buttons.add(types.InlineKeyboardButton(
            text=frases_dict["contact"][lang], callback_data="sup"))
        bot.send_message(call.message.chat.id,
                         messages.pay_type[lang], reply_markup=buttons)

    elif call.data in ["1", "2", "3", "4", "5"]:

        # User has already rated
        if get_info("rate", "tg_id", call.message.chat.id) != "0":
            bot.send_message(call.message.chat.id,
                             frases_dict["ar_rate"][lang])
            return

        rating = call.data

        # Ask user to make review if he gave the highest rate
        if rating == "5":
            buttons.add(types.InlineKeyboardButton(
                text=frases_dict["leave_feedback"][lang], url=config.review_link))
            bot.send_message(call.message.chat.id, frases_dict["feedback_bonus"][lang],
                             reply_markup=buttons, parse_mode='Markdown')
        # Ask user to write feedback
        else:
            buttons.add(types.InlineKeyboardButton(
                text=frases_dict["give_wish"][lang], callback_data="get_better"))
            bot.send_message(
                call.message.chat.id, frases_dict["give_wish_question"][lang], reply_markup=buttons)

        bot.send_message(config.group_id, f"Клиент `{call.message.chat.id}` поставил вам {rating}",
                         parse_mode='Markdown')
        update_clients(["tg_id", call.message.chat.id], ["rate", rating])

    # User chose tariff he wants to buy, send him buttons to choose tariff duration in days (ascending order)
    # Temporarily off
    elif False and re.fullmatch(r'[РЮ]-[123]+', call.data):
        currency, tariff_id = call.data.split('-')
        tariffs_list = get_tariffs(['tariff', tariff_id], [
            'currency', currency])
        for price, tariff_id, days, currency, desc in sorted(tariffs_list, key=lambda x: int(x[2])):
            # Telegram does not support prices lower than 60 rub.
            if int(price) < 60:
                continue
            # Choose correct form of 'день' word
            if days[-1] == '1':
                day_word = 'день'
            elif days[-1] in '234':
                day_word = 'дня'
            else:
                day_word = 'дней'
            buttons.add(types.InlineKeyboardButton(text=f"{days} {day_word}",
                                                   callback_data=f"{currency}-{tariff_id}-{days}"))
        bot.send_message(call.message.chat.id, f"Выберите, на сколько дней вы хотите продлить тариф {tariff_id}",
                         reply_markup=buttons)

    # User chose tariff duration in days, send him payment button
    # Temporarily off
    elif False and re.fullmatch(r'[РЮ]-[123]+-[0-9]+', call.data):
        currency, tariff_id, days = call.data.split('-')
        specific_tariff = get_tariffs(['tariff', tariff_id], [
            'currency', currency], ['days', days])[0]
        price = int(specific_tariff[0])
        prices = [types.LabeledPrice(
            label=f'Тариф {tariff_id} на {days} дней', amount=price * 100)]
        bot.send_invoice(call.message.chat.id, title=f"Тариф {tariff_id}",
                         description='Plati',
                         provider_token=config.pay_token,
                         currency='rub',
                         prices=prices,
                         start_parameter='payment',
                         invoice_payload='HAPPY FRIDAYS COUPON')
    elif call.data == "trial_ok":
        email = db_find_value("tg_id", call.message.chat.id)["email"]
        link = add_trial_tg(email)
        if link != "":
            close_dialogue("tg_id", call.message.chat.id, pay=True)
            bot.send_message(call.message.chat.id, text=message_trial_period_ok(
                call.message, link), parse_mode='MarkdownV2')
        else:
            close_dialogue("tg_id", call.message.chat.id)
            bot.send_message(call.message.chat.id,
                             message_trial_period_err[lang])
        initial_buttons(call.message)
    elif call.data == "trial_cancel":
        bot.send_message(call.message.chat.id,
                         message_trial_period_cancel[lang])
        initial_buttons(call.message)
    elif call.data == "ch_other":
        bot.edit_message_text("Вы выбрали \"другое\"", chat_id=call.message.chat.id,
                              message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, curr_text.text_other, reply_markup=curr_text.cancel_btn())
        curr_temp[call.message.chat.id]["state"] = "other"
        curr_temp[call.message.chat.id]["type"] = "другое"
    elif call.data == "ch_buy_yan":
        bot.edit_message_text("Вы покупаете юани", chat_id=call.message.chat.id,
                              message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, curr_text.buy_yuan_1, reply_markup=curr_text.cancel_btn())
        curr_temp[call.message.chat.id]["state"] = "count"
        curr_temp[call.message.chat.id]["type"] = "покупка"
    elif call.data == "ch_sell_yan":
        bot.edit_message_text("Вы продаете юани", chat_id=call.message.chat.id,
                              message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, curr_text.sell_yuan_1, reply_markup=curr_text.cancel_btn())
        curr_temp[call.message.chat.id]["state"] = "count"
        curr_temp[call.message.chat.id]["type"] = "продажа"
    elif call.data in curr_text.cb_choices.keys():
        curr_temp[call.message.chat.id]["valuta"] = curr_text.cb_choices[call.data]
        curr_temp[call.message.chat.id]["state"] = "urgency"
        bot.edit_message_text(curr_text.yuan_3, chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=curr_text.urgency_btns())
    elif call.data in curr_text.urg.keys():
        curr_temp[call.message.chat.id]["urgency"] = curr_text.urg[call.data]
        curr_temp[call.message.chat.id]["state"] = "requisites"
        if curr_temp[call.message.chat.id]["type"] == "покупка":
            bot.edit_message_text(curr_text.buy_yuan_4, chat_id=call.message.chat.id,
                                  message_id=call.message.message_id)
        elif curr_temp[call.message.chat.id]["type"] == "продажа":
            bot.edit_message_text(curr_text.sell_yuan_4, chat_id=call.message.chat.id,
                                  message_id=call.message.message_id)


@bot.message_handler(func=check_mailing,
                     content_types=['text', 'photo', 'video', 'voice', 'audio', 'sticker', 'document'])
def mailing(message):
    """ Sends a message to clients with selected tariffs """
    # lang = get_user_lang(message.from_user.id)

    txt = message.text or message.caption

    if txt == "/рассылка":
        bot.send_message(message.chat.id, messages.mailing_tariffs)
        return

    client_text = message.reply_to_message.text

    if client_text == messages.mailing_tariffs:
        temp['tariffs'] = [i.lower() for i in txt.split()]
        bot.send_message(message.chat.id, messages.mailing_message)

    elif client_text == messages.mailing_message:
        temp['message_id'] = message.message_id
        temp['mail_text'] = txt
        bot.send_message(message.chat.id, f"Следующие тарифы: {', '.join(temp['tariffs'])}\n"
                                          f"Получат сообщение:\n{txt}\n\n"
                                          f"Продолжить? Да/Нет ответом.\n"
                                          f"Чтобы отправить ТОЛЬКО в телеграм или вконтакте, ответьте тг/вк")

    elif client_text.startswith("Следующие тарифы:"):
        if txt.lower() in ["да", "вк", "тг"]:

            if not temp['tariffs'] or not temp['mail_text']:
                bot.send_message(message.chat.id, "Не выбраны тарифы/текст!")
                return
            if txt.lower() == "вк":
                spam(temp['tariffs'], temp['mail_text'],
                     message.chat.id, vk_only=True)
            elif txt.lower() == 'тг':
                spam(temp['tariffs'], temp['mail_text'],
                     message.chat.id, tg_only=True)
            else:
                spam(temp['tariffs'], temp['mail_text'], message.chat.id)
            bot.send_message(message.chat.id, "Рассылка отправлена")

        elif txt.lower() == "нет":
            bot.send_message(message.chat.id, "Рассылка отменена")
            temp['tariffs'], temp['mail_text'] = [], ''

        else:
            bot.send_message(message.chat.id, "Не понял, повторите")


@bot.message_handler(func=check_mail_edit)
def mail_edit(message):
    """ Allows bot owner to edit database, deleting row with wrong email and copying IDs to row with correct email
        Start with bot command '/почта', then reply to every bot message """

    if message.text == "/почта":
        temp["true_email"] = ""
        temp["wrong_email"] = ""
        bot.send_message(message.chat.id, messages.edit_wrong_mail)
        return

    reply_text = message.reply_to_message.text

    # First, you must enter wrong email address, existing in DB
    if reply_text == messages.edit_wrong_mail:
        wrong_email_info = db_find_value("email", message.text.lower())

        # Wrong email not found in DB
        if not wrong_email_info:
            bot.send_message(message.chat.id, "Такой почты нет в базе!")
            return

        # Save email info to temp
        temp['wrong_email'] = list(wrong_email_info.values())

        # Message for the next step
        bot.send_message(message.chat.id, messages.edit_true_mail)

    # Second, you must enter correct email address, existing in DB
    elif reply_text == messages.edit_true_mail:

        # No info about wrong email in temp
        if not temp['wrong_email']:
            bot.send_message(message.chat.id, "Не указан неверный email")
            return

        true_email_info = db_find_value("email", message.text.lower())

        # Correct email not found in DB
        if not true_email_info:
            bot.send_message(message.chat.id, "Такой почты нет в базе!")
            return

        temp['true_email'] = list(true_email_info.values())
        t = temp['true_email']
        w = temp['wrong_email']

        # Send two messages with DB info about wrong and correct email so we can check everything
        bot.send_message(message.chat.id, f"Данные неправильной почты:\nemail = {w[0]}\ndate = {w[1]}\n"
                                          f"tariff = {w[2]}\nsub = {w[3]}\ntg_id = {w[4]}\n"
                                          f"vk_id = {w[5]}\nfb_id = {w[6]}")

        bot.send_message(message.chat.id, f"Данные правильной почты:\nemail = {t[0]}\ndate = {t[1]}\n"
                                          f"tariff = {t[2]}\nsub = {t[3]}\n"
                                          f"tg_id = {t[4]}\nvk_id = {t[5]}\nfb_id = {t[6]}")

        # Return if wrong and correct emails have different IDs for the same messenger (tg/vk/fb)
        if w[4] != "0" != t[4] and w[4] != t[4] \
                or w[5] != "0" != t[5] and w[5] != t[5] \
                or w[6] != "0" != t[6] and w[6] != t[6]:
            bot.send_message(
                message.chat.id, "У этих почт разные айди для одного способа связи, надо разбираться\n")
            return

        # Send message, asking to confirm editing
        bot.send_message(message.chat.id, messages.edit_confirm)

    elif reply_text == messages.edit_confirm:

        # Editing confirmed
        if message.text.lower() == "да":
            t = temp['true_email']
            w = temp['wrong_email']

            # No info about wrong or correct email in temp
            if not t or not w:
                bot.send_message(message.chat.id, "Не указаны почты")
                return

            # Record this change to log
            with open("edit_log.txt", "a+") as file:
                file.write(f"---------------------------\n{datetime.datetime.today()}\n"
                           f"wrong email = {w[0]}\ntrue email = {t[0]}\n")

            tg_id, vk_id, fb_id = w[4], w[5], w[6]
            t_mail = t[0]

            update_clients(["email", t_mail], ["state", "CLOSED"], [
                "rate", "5"], ["review_time", "0"])

            # Check if ID that we want to copy != 0 and not the same with correct email ID
            if tg_id not in ["0", t[4]]:
                update_clients(["email", t_mail], ["tg_id", tg_id])
                print(f"Заменили tg_id {t[4]} на {tg_id}\n")

            if vk_id not in ["0", t[5]]:
                update_clients(["email", t_mail], ["vk_id", vk_id])
                print(f"Заменили vk_id {t[5]} на {vk_id}\n")

            if fb_id not in ["0", t[6]]:
                update_clients(["email", t_mail], ["fb_id", fb_id])
                print(f"Заменили fb_id {t[6]} на {fb_id}\n")

            bot.send_message(message.chat.id, delete_client("email", w[0]))
            print(f"Удалили запись с почтой {w[0]}")
            temp['wrong_email'], temp['true_email'] = "", ""

        # Editing cancelled
        elif message.text.lower() == "нет":
            bot.send_message(message.chat.id, "Замена почты отменена")
            temp['wrong_email'], temp['true_email'] = "", ""
        else:
            bot.send_message(message.chat.id, "Не понял, повторите")


@bot.message_handler(func=lambda message: check_mail_edit(message, '/изменить'))
def mail_edit(message):
    """ Allows bot owner to edit database, deleting row with wrong email and copying IDs to row with correct email
        Start with bot command '/почта', then reply to every bot message """

    if message.text == "/изменить":
        bot.send_message(message.chat.id, messages.edit_by_mail_msg)
        return

    text = message.text.lower()

    if not re.fullmatch(r'\S+@\S+;\n((date|tariff|sub|tg_id|vk_id|fb_id)::\S+;\n?)+', text):
        bot.send_message(message.chat.id, messages.edit_format_error)
        return

    search_email = text.split(';')[0]
    args = text.split(';')[1:-1]
    args = [
        [i.strip() for i in line.split('::')]
        for line in args
    ]

    update_clients(['email', search_email], *args)

    args_str = '\n'.join(['::'.join(line) for line in args])
    msg = f"""Изменили запись в базе для почты {search_email}\nНовые данные:\n{args_str}"""

    bot.send_message(message.chat.id, msg)


@bot.message_handler(func=lambda message: message.chat.id in [config.group_id, config.exchange_id],
                     content_types=['text', 'audio', 'document', 'photo', 'sticker', 'voice', 'video'])
def support_group(message):
    """ Handle all messages in support group """
    chat_id = message.chat.id
    exch_flag = True if chat_id == config.exchange_id else False

    # Bot info message
    if message.text and message.text.lower() == "/info":
        bot.send_message(chat_id, messages.info)
    # change wechat info
    elif message.text and message.text.lower().split()[0] == "/wechange":
        currency_change_queries.update_wechat(message.text)
        bot.send_message(chat_id, "Успешно изменено")
    # Message is reply to some message
    elif message.reply_to_message:
        client_text = message.reply_to_message.text or message.reply_to_message.caption

        if not client_text:
            pass

        # Reply object message was forwarded from tg
        elif client_text and client_text.endswith("Telegram") or client_text.endswith("Telegram\U00002705"):

            tg_id = client_text.split()[-2]

            # User id does not fit 'one or more numeral' regexp
            if not re.fullmatch(r"[0-9]+", str(tg_id)):
                bot.send_message(chat_id, "Не удалось отправить сообщение. "
                                          "Скорее всего это закрытый аккаунт без айди в подписи")
                return

            # Close dialogue
            if message.text and message.text.lower() in ["пока", "/пока", "off", "конец", "/q"]:
                close_dialogue("tg_id", tg_id, curr=exch_flag)
                if exch_flag:
                    select_all_exch()
            # Close payment dialogue
            elif message.text and message.text.lower() in ["/оплата", "оп"]:
                close_dialogue("tg_id", tg_id, pay=True, curr=exch_flag)
            # Close dialogue silently
            elif message.text and message.text.lower() == "/закрыть":
                close_dialogue("tg_id", tg_id, silent=True, curr=exch_flag)
                if exch_flag:
                    select_all_exch()
            # Check if message was forwarded by bot, not by other user
            elif message.reply_to_message.from_user.id == config.bot_id:
                # Finally, send answer to client :)
                copy_send_message(tg_id, message.chat.id, message.message_id)
                if exch_flag:
                    open_dialogue("tg_id", tg_id, state="CURR")
                else:
                    open_dialogue("tg_id", tg_id)

        # Reply object message was forwarded from VK
        elif client_text and client_text.endswith("Vkontakte") or client_text.endswith("Vkontakte\U00002705"):
            vk_id = client_text.split()[-2]

            if message.text and message.text.lower() in ["пока", "off", "конец", "/q"]:
                close_dialogue("vk_id", vk_id)
            elif message.text and message.text.lower() in ["/оплата", "оп"]:
                close_dialogue("vk_id", vk_id, pay=True)
            elif message.text and message.text.lower() == "/закрыть":
                close_dialogue("vk_id", vk_id, silent=True)
            else:
                tg_to_vk(message, vk_id)
                open_dialogue("vk_id", vk_id)

        # Reply object message was forwarded from FB
        elif client_text and client_text.endswith("Facebook"):
            fb_id = client_text.split()[-2]

            if message.text and message.text.lower() in ["пока", "/пока", "off", "конец", "/q"]:
                close_dialogue("fb_id", fb_id)
            elif message.text and message.text.lower() in ["/оплата", "оп"]:
                close_dialogue("fb_id", fb_id, pay=True)
            elif message.text and message.text.lower() == "/закрыть":
                close_dialogue("fb_id", fb_id, silent=True)
            else:
                tg_to_fb(message, fb_id)

        # my code
        elif client_text and client_text.endswith("Web_client"):
            from src import data_structs as ds

            replied_message = message.reply_to_message.text

            if replied_message is None:
                replied_message = message.reply_to_message.caption

            reply_email = helpers.get_email_from_message(replied_message)

            ws_message = json.dumps({'from': 'bot', 'message': message.text})

            import asyncio
            asyncio.run(ds.send_ws_msg(reply_email, ws_message))

    # Message is not reply to some message
    else:

        # Message text is dialogue closing command
        if message.text and message.text.lower().split()[0] in ["пока", "/пока", "off", "конец", "/q"]:

            # If not replying to some message, closing message must be exactly 2 words
            # and contain ID of user whose dialogue we want to close
            if len(message.text.lower().split()) != 2:
                bot.send_message(message.chat.id, "Отправьте команду и айди через пробел, например:\n"
                                                  "Пока 1234567")
                return

            # We don't know which messenger this id belongs to, so just try to close this ID for every type
            for id_type in ["tg_id", "vk_id", "fb_id"]:
                close_dialogue(id_type, message.text.lower().split()[1])

        elif message.text and message.text.lower().split()[0] in ["/оплата", "оп"]:
            if len(message.text.lower().split()) != 2:
                bot.send_message(message.chat.id, "Отправьте команду и айди через пробел, например:\n"
                                                  "/оплата 1234567")
                return

            for id_type in ["tg_id", "vk_id", "fb_id"]:
                close_dialogue(
                    id_type, message.text.lower().split()[1], pay=True)

        elif message.text and message.text.lower().split()[0] == "/закрыть":
            splitted = message.text.lower().split()
            if len(splitted) != 2:
                bot.send_message(message.chat.id, "Отправьте команду и айди через пробел, например:\n"
                                                  "/закрыть 1234567")
                return

            target_id = splitted[1]
            if target_id in ['все', 'всё']:
                close_all_dialogues()
            else:
                for id_type in ["tg_id", "vk_id", "fb_id"]:
                    close_dialogue(id_type, message.text.lower().split()[
                        1], silent=True)


@bot.message_handler(
    func=lambda message: get_info("state", "tg_id", message.chat.id) in ["OPEN", "REMINDED", "PAY", "CURR"],
    content_types=['text', 'photo', 'video', 'voice', 'audio', 'sticker', 'document'])
def forward_to_support(message):
    """ Forward all clients messages to support group if dialogue is open
        Also send to support info about client's tariff """

    user_info = db_find_value("tg_id", message.chat.id)
    user_state = user_info['state']

    # transfer client's message to support group
    if user_state == "CURR":
        group_id = config.exchange_id
        update_clients(["tg_id", message.chat.id], ["received", "YES"])
        tg_to_tg(group_id, message, curr_change=True)
    else:
        group_id = config.group_id
        tg_to_tg(group_id, message)

    # Client sent a message after being reminded about the payment, open dialogue
    if user_state == "REMINDED":
        open_dialogue("tg_id", message.chat.id, state="PAY")
        if message.photo:
            filename = save_file(
                message, folder=config.pay_imgs_path, check=True)
            autopay(message.chat.id, 'tg_id', filename)

    # Client sent a photo after he has chosen the payment option. Consider this photo as payment screenshot
    elif user_state == "PAY":
        if message.photo:
            filename = save_file(
                message, folder=config.pay_imgs_path, check=True)
            autopay(message.chat.id, 'tg_id', filename)

    # Notify client that his message was received (once per dialogue)
    if user_info['received'] == "NO":
        bot.send_message(message.chat.id, "Ваше сообщение передано в поддержку. "
                                          "Мы постараемся ответить как можно быстрее!")
        update_clients(["tg_id", message.chat.id], ["received", "YES"])


@bot.message_handler(func=lambda message: get_info("state", "tg_id", message.chat.id) == "CLOSED",
                     content_types=['text', 'photo', 'video', 'voice', 'audio', 'sticker', 'document'])
def push_something(message):
    """ If user identified and dialogue is closed, ask him to use buttons """
    lang = get_user_lang(message.from_user.id)
    initial_buttons(message, send_text=messages.push_buttons[lang])


@bot.message_handler(func=lambda message: get_info("state", "tg_id", message.chat.id) == "ONE MESSAGE",
                     content_types=['text', 'photo', 'video', 'voice', 'audio', 'sticker', 'document'])
def one_message_pass(message):
    """ User pushed the feedback button after previous support conversation was closed.
        Suppose user entering one-message review """
    lang = get_user_lang(message.from_user.id)
    time_past = int(time.time()) - \
                int(get_info("review_time", "tg_id", message.chat.id))

    # If user pushed the button more than a day ago, don't send his message to support
    if time_past // 3600 >= 24:
        bot.send_message(message.chat.id, messages.buttons_menu[lang])

    else:
        tg_to_tg(config.group_id, message, review=True)
        bot.send_message(message.chat.id, "Спасибо за отзыв!")

    update_clients(["tg_id", message.chat.id], ["state", "CLOSED"])


# --------------------------------------------------
def main():
    while True:
        try:
            print('\nTelegram running')
            bot.polling(none_stop=True, interval=0, timeout=30)

        except Exception as e:
            print('Ошибка:\n', traceback.format_exc())
            print("TG error, restarting")
            print(e)
            bot.stop_polling()
            log_report("TG", e)
            time.sleep(3)
        else:
            bot.stop_polling()
