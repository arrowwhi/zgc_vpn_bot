from telebot import types
import helpers
import currency_helpers

text_registration = "Укажите ваш Wechat ID или номер телефона привязанный к аккаунту, " \
                    "чтобы мы могли с вами связаться и перевести или принять деньги."

text_reg_error = "пожалуйста, укажите номер в правильном формате"

text_first_msg = "Выберите, что вы хотите сделать:"


def text_first_msg_btns():
    buttons = types.InlineKeyboardMarkup()
    buttons.add(types.InlineKeyboardButton(text="купить юань", callback_data="ch_buy_yan"))
    buttons.add(types.InlineKeyboardButton(text="продать юань", callback_data="ch_sell_yan"))
    buttons.add(types.InlineKeyboardButton(text="другая валюта", callback_data="ch_other"))
    return buttons


def yuan_0():
    q1, q2 = currency_helpers.get_rate()
    m = f"Средний курс:\n" \
        f"Покупка: {q1} рублей/юань\n" \
        f"Продажа: {q2} рублей/юань\n" \
        f"\n\nКонечный курс будет зависеть от того, сколько валюты вы хотите обменять."
    return m


sell_yuan_1 = "Укажите, сколько юаней вы хотите продать"
buy_yuan_1 = "Укажите, сколько юаней вы хотите купить"

sell_yuan_2 = "Какую валюту вы хотите получить взамен?"
buy_yuan_2 = "За какую валюту хотите получить юани?"

yuan_3 = "Насколько срочно нужно сделать перевод?"

buy_yuan_4 = "Укажите способ получения юаней. Алипэй/Вичат/Карта/Фирма или завод. Также укажите реквизиты, " \
             "QR код на оплату/добавление в друзья/способ связи с заводом или фирмой."

sell_yuan_4 = "Укажите реквизиты куда хотите получить деньги, например:\
- номер телефона \
- номер карты \
- реквизиты \
Обязательно укажите название банка"

change_currency_final = "Ваша заявка принята! В ближайшее время с вами свяжется менеджер, " \
                        "предоставит курс и реквизиты для перевода.\n\n ⚠️ Общайтесь с оператором только в этом чате. " \
                        "Если вам напишут по поводу обмена с другого аккаунта, это мошенники."

text_other = """Укажите по списку:
1) Валюта, которую хотите продать
2) Валюта, которую хотите купить
3) Срочность перевода
4) Реквизиты, с которых планируете отправлять валюту 
5) Реквизиты, на которые хотите получить валюту."""


def curr_choice_btns():
    buttons = types.InlineKeyboardMarkup()
    buttons.add(types.InlineKeyboardButton(text="Рубли", callback_data="ch_rub"))
    buttons.add(types.InlineKeyboardButton(text="Гривны", callback_data="ch_gri"))
    buttons.add(types.InlineKeyboardButton(text="USDT", callback_data="ch_usdt"))
    buttons.add(types.InlineKeyboardButton(text="Лиры", callback_data="ch_lir"))
    buttons.add(types.InlineKeyboardButton(text="Лари", callback_data="ch_lari"))
    buttons.add(types.InlineKeyboardButton(text="Другая валюта", callback_data="ch_other"))
    return buttons


cb_choices = {"ch_rub": "рубли", "ch_gri": "гривны", "ch_usdt": "usdt", "ch_lir": "лиры", "ch_lari": "лари"}

urg = {"ch_immed": "Срочно", "ch_2_hours": "В течение 2-х часов", "ch_day": "В течение дня"}


def urgency_btns():
    buttons = types.InlineKeyboardMarkup()
    buttons.add(types.InlineKeyboardButton(text="Срочно", callback_data="ch_immed"))
    buttons.add(types.InlineKeyboardButton(text="В течение 2-х часов", callback_data="ch_2_hours"))
    buttons.add(types.InlineKeyboardButton(text="В течение дня", callback_data="ch_day"))
    return buttons


def get_support_msg(message, user_info, uncompleted=False):
    check = "\U00002705" if helpers.get_info(
        "verified", "tg_id", message.chat.id) else ''
    unc = "\n\U0000274cОбмен отменен! ОТМЕНЕН это значит что человек начал обмен и на каком-то моменте решил нажать " \
          "кнопку \"отменить\" и пошел дальше по другим делам \n" if uncompleted else ""
    a = f"""\U0001F4B1 Exchange 
\U0001F4AC{message.from_user.first_name} {message.from_user.last_name}
{unc}
    Названный курс: {user_info.get("exc", "")}
    Что хочет: {user_info.get("type", "")}
    Количество юаней: {user_info.get("count", "")}
    Обратная валюта: {user_info.get("valuta", "")}
    Срочность: {user_info.get("urgency", "")}
    Реквизиты out: {user_info.get("requisites", "")}
    Дополнительная информация: {user_info.get("dop_info", "")}

    {message.chat.id} Telegram{check}
    """
    return a


def get_final_message(user_info):
    a = f"""Ваша заявка:
    Тип заявки: 
    {user_info.get("type", "")} юань
    
    Количество юаней: 
    {user_info.get("count", "")}
    
    Выбранная валюта: 
    {user_info.get("valuta", "")}
    
    Срочность: 
    {user_info.get("urgency", "")}
    
    Реквизиты для получения:
    {user_info.get("requisites", "")}
    
    Если вы хотите что-то добавить, или одно из полей введено ошибочно - напишите об этом. Если все в порядке - 
    нажмите "Отправить заявку"""
    return a


def cancel_btn(final=False):
    markup_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if final:
        item_confirm = types.InlineKeyboardButton("\u2705 Отправить заявку")
        markup_buttons.add(item_confirm)
    # item_pay = types.InlineKeyboardButton("\U00002753 Связаться с поддержкой")
    # markup_buttons.add(item_pay)
    item_dialogue = types.InlineKeyboardButton("\U0001F6AB Отменить обмен")
    markup_buttons.add(item_dialogue)
    return markup_buttons
