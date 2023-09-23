import gspread
from telebot import types
from src.helpers import bot, open_dialogue
import uuid
from src.change_language import get_user_lang


def add_trial_check(email):
    mail = email.strip()

    gc = gspread.service_account(
        filename='/root/sheetvenv/service_account.json')
    sh = gc.open_by_key('1i_T4pSiuCqXt8xubOH7YL6BNMXXcBcX5WgfX5zCLPJE')
    fil = sh.worksheet('Filters')
    filavalues = fil.get_all_values()

    emaillist = []
    filelist = []
    autoemaillist = []
    # Get column values
    for i, x in enumerate(filavalues):
        # Start from row 3
        if i >= 2:
            if x[0]:
                emaillist.append(x[0])
            if x[2]:
                filelist.append(x[2])
            if x[6]:
                autoemaillist.append(x[6])

    halfemail = mail.split('@', 1)[1]

    if halfemail in emaillist or mail.lower() in list(map(lambda x: x.lower(), autoemaillist)):
        print('Filtered by email: {}'.format(mail))
        row = len(filelist) + 3
        fil.update_cell(row, 3, mail)
        return False
    return True


accurl = 'https://zgc.su/account/'


def add_trial_tg(email):
    mail = email.strip()

    gc = gspread.service_account(
        filename='/root/sheetvenv/service_account.json')
    sh = gc.open_by_key('1i_T4pSiuCqXt8xubOH7YL6BNMXXcBcX5WgfX5zCLPJE')
    fil = sh.worksheet('Filters')
    filavalues = fil.get_all_values()

    emaillist = []
    filelist = []
    autoemaillist = []
    # Get column values
    for i, x in enumerate(filavalues):
        # Start from row 3
        if i >= 2:
            if x[0]:
                emaillist.append(x[0])
            if x[2]:
                filelist.append(x[2])
            if x[6]:
                autoemaillist.append(x[6])

    halfemail = mail.split('@', 1)[1]

    if halfemail in emaillist or mail.lower() in list(map(lambda x: x.lower(), autoemaillist)):
        print('Filtered by email: {}'.format(mail))
        row = len(filelist) + 3
        fil.update_cell(row, 3, mail)
        return ""

    # Generate random uuid
    randuuid = str(uuid.uuid4())

    with open("/root/sheetvenv/trial.txt", "a") as f:
        f.write(email + ";" + randuuid)

    return accurl + randuuid


def trial_period_offer(message, text):
    open_dialogue("tg_id", message.chat.id)
    buttons = types.InlineKeyboardMarkup()
    buttons.add(types.InlineKeyboardButton(
        text="Получить", callback_data="trial_ok"))
    buttons.add(types.InlineKeyboardButton(
        text="Отказаться", callback_data="trial_cancel"))
    bot.send_message(message.chat.id, text, reply_markup=buttons)


message_trial_period_button = {"ru": "Вы можете оформить пробный период на 3 дня. Хотите?",
                               "en": "You can sign up for a 3-day trial period. Do you want to?"}
message_trial_period_first = {"ru": "Мы предлагаем вам протестировать наш VPN и получить пробный период на 3 дня",
                              "en": "We invite you to test our VPN and get a trial period of 3 days"}


def message_trial_period_ok(message, link):
    lang = get_user_lang(message.chat.id)
    q = {"ru": """
Готово! Ваша пробная подписка:

""" + link + """

☝️ Вам не нужно её открывать, просто скопируйте и добавьте в приложение по инструкции.
🤔 Как добавить подписку?
Следуйте инструкции на сайте:
•[Для Android](https://zgcvpn.ru/android)   
•[Для Mac OS](https://zgcvpn.ru/mac)
•[Для Windows](https://zgcvpn.ru/windows)
•[Для IPhone (IOS)](https://zgcvpn.ru/ios)
•[Другие устройства](https://zgcvpn.ru/download)

🙈 Возникли трудности? Нажмите справа в меню "связаться с поддержкой" и мы поможем!

""", "en": """
Completed! Your trial subscription:

""" + link + """

☝️ You don't need to open it, just copy and add to the application according to the instructions.
🤔 How to add a subscription?
Follow the instructions on the site:
•[For Android](https://zgcvpn.ru/android/en)
•[For Mac OS](https://zgcvpn.ru/mac/en)
•[For Windows](https://zgcvpn.ru/windows/en)
•[For iPhone (IOS)](https://zgcvpn.ru/ios/en)
•[Other devices](https://zgcvpn.ru/download/en)

🙈 Any difficulties? Click on the right in the menu "contact support" and we will help!
    """}

    return q[lang]


message_trial_period_err = {
    "ru": "Вы уже брали пробный период. Чтобы воспользоваться нашим сервисом, вам необходимо оплатить тариф.",
    "en": "You have already taken a trial period. To use our service, you need to pay a tariff."}

message_trial_period_cancel = {"ru": "Если передумаете - нажмите на кнопку \"Пробный период\".",
                               "en": "If you change your mind, click on the \"Trial period\" button."}
