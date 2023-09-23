import gspread
from helpers import db_find_value
user_lang = {}


def set_user_lang(id):
    lang = get_user_lang(id)
    email = db_find_value("tg_id", id)["email"]
    gc = gspread.service_account(
        filename='/root/sheetvenv/service_account.json')
    sh = gc.open_by_key('1i_T4pSiuCqXt8xubOH7YL6BNMXXcBcX5WgfX5zCLPJE')
    fil = sh.worksheet('Clients')
    clients = fil.get_all_values()
    for i in range(len(clients)):
        if clients[i][3] == email or clients[i][4] == email:
            buff = clients[i][10]
            if buff[:2] == "en":
                fil.update('K'+str(i+1), buff[2:])
                user_lang[id] = "ru"
            else:
                fil.update('K'+str(i+1), "en"+buff)
                user_lang[id] = "en"


def get_user_lang(id):
    return 'ru'
    if not user_lang.get(id):
        email = db_find_value("tg_id", id)["email"]
        gc = gspread.service_account(
            filename='/root/sheetvenv/service_account.json')
        sh = gc.open_by_key('1i_T4pSiuCqXt8xubOH7YL6BNMXXcBcX5WgfX5zCLPJE')
        fil = sh.worksheet('Clients')
        clients = fil.get_all_values()
        for i in clients:
            if i[4].lower() == email or i[3].lower() == email:
                if i[10].strip()[:2] == "en":
                    user_lang[id] = "en"
                else:
                    user_lang[id] = "ru"
    return user_lang.get(id, 'ru')


frases_dict = {}

frases_dict["payment"] = {}
frases_dict["payment"]["ru"] = "\U0001F4B4 Оплата"
frases_dict["payment"]["en"] = "\U0001F4B4 Payment"

frases_dict["trial"] = {}
frases_dict["trial"]["ru"] = "\U0001F193 Пробный период"
frases_dict["trial"]["en"] = "\U0001F193 Trial period"

frases_dict["knowmore"] = {}
frases_dict["knowmore"]["ru"] = "\U0001F4F0 Узнать больше"
frases_dict["knowmore"]["en"] = "\U0001F4F0 Know more"

frases_dict["forturk"] = {}
frases_dict["forturk"]["ru"] = "\U0001F1F9\U0001F1F2Для Туркменистана"
frases_dict["forturk"]["en"] = "\U0001F1F9\U0001F1F2For Turkmenistan"

frases_dict["coop"] = {}
frases_dict["coop"]["ru"] = "\U0001F91D Сотрудничество"
frases_dict["coop"]["en"] = "\U0001F91D Cooperation"

frases_dict["contact"] = {}
frases_dict["contact"]["ru"] = "\U00002753 Связаться с поддержкой"
frases_dict["contact"]["en"] = "\U00002753 Connect support"

frases_dict["rub-gri"] = {}
frases_dict["rub-gri"]["ru"] = "В рублях ₽ или в гривнах ₴"
frases_dict["rub-gri"]["en"] = "In rubles ₽ or hryvnias ₴"

frases_dict["uan"] = {}
frases_dict["uan"]["ru"] = "В юанях ¥"
frases_dict["uan"]["en"] = "In yuan ¥"

frases_dict["blog"] = {}
frases_dict["blog"]["ru"] = "Блог"
frases_dict["blog"]["en"] = "Blog"

frases_dict["blog_text"] = {}
frases_dict["blog_text"]["ru"] = "Узнайте как заблокировать рекламу, какие появились сервера и многое другое"
frases_dict["blog_text"]["en"] = "Learn how to block ads, what servers have appeared and more"

frases_dict["tm_site"] = {}
frases_dict["tm_site"]["ru"] = "Сайт обслуживания"
frases_dict["tm_site"]["en"] = "Service Site"

frases_dict["tm_how"] = {}
frases_dict["tm_how"]["ru"] = "Как подключить?"
frases_dict["tm_how"]["en"] = "How to connect?"

frases_dict["go_coop"] = {}
frases_dict["go_coop"]["ru"] = "Сделать предложение"
frases_dict["go_coop"]["en"] = "Make an offer"

frases_dict["hello_product"] = {}
frases_dict["hello_product"]["ru"] = 'Здравствуйте! Укажите, пожалуйста, продукт и вопросы по нему'
frases_dict["hello_product"]["en"] = 'Hello! Please indicate the product and questions about it'

frases_dict["ar_rate"] = {}
frases_dict["ar_rate"]["ru"] = "Вы уже поставили оценку, спасибо!"
frases_dict["ar_rate"]["en"] = "You have already rated, thank you!"

frases_dict["leave_feedback"] = {}
frases_dict["leave_feedback"]["ru"] = "\U0001F49B Оставить отзыв"
frases_dict["leave_feedback"]["en"] = "\U0001F49B Leave feedback"


frases_dict["feedback_bonus"] = {}
frases_dict["feedback_bonus"]["ru"] = "Если вам понравился наш сервис - оставьте отзыв,и мы предоставим вам 10 дней бесплатного VPN!\n\n_Когда оставите отзыв, свяжитесь с нами для получения бонуса_",
frases_dict["feedback_bonus"]["en"] = "If you like our service - leave a review, and we will give you 10 days of free VPN!\n\n_When you leave a review, contact us for a bonus_",

frases_dict["give_wish"] = {}
frases_dict["give_wish"]["ru"] = "\U0001F4A1 Оставить пожелание"
frases_dict["give_wish"]["en"] = "\U0001F4A1 Give a wish"

frases_dict["give_wish_question"] = {}
frases_dict["give_wish_question"]["ru"] = "Мы можем что-то улучшить в обслуживании?"
frases_dict["give_wish_question"]["en"] = "Can we improve something in the service?"

frases_dict["init_setup"] = {}
frases_dict["init_setup"]["ru"] = "Первичная настройка"
frases_dict["init_setup"]["en"] = "Initial setup"

frases_dict["btn_other"] = {}
frases_dict["btn_other"]["ru"] = "Другое"
frases_dict["btn_other"]["en"] = "Other"

frases_dict["srochno"] = {}
frases_dict["srochno"]["ru"] = "Срочная связь"
frases_dict["srochno"]["en"] = "Urgent Communication"

frases_dict["your_sub"] = {}
frases_dict["your_sub"]["ru"] = "\U000026A1 Ваша подписка: "
frases_dict["your_sub"]["en"] = "\U000026A1 Your subscription: "
