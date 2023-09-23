import messages

commands = '''
Оплата, В рублях ₽ или в гривнах ₴, В юанях ¥, Связаться с поддержкой,
Пробный период, 
Узнать больше, Блог,
Для Туркменистана, 
Сотрудничество, 
ZGC SHOP, 
Связаться с поддержкой

'''

# варианты ответа через 2 запятые
command_answers = \
    {
        "/Оплата": {"answer": messages.pay_type,
                    "commands": [("В рублях ₽ или в гривнах ₴", '/rub'), ("В юанях ¥", "/yuan"),
                                 ("Связаться с поддержкой", '/Связаться с поддержкой')]},
        "/Пробный период": {"answer": messages.ru_site_trial_text,
                            "commands": [('http://zgcvpn.ru', 'http://zgcvpn.ru'), ("Оплата", '/Оплата'),
                                         ("Связаться с поддержкой", '/Связаться с поддержкой')]},
        "/Узнать больше": {"answer": "Узнайте как заблокировать рекламу, какие появились сервера и многое другое",
                           "commands": [["Блог", 'https://market.zgc.su/zgcvpnblog']]},
        "/Для Туркменистана": {"answer": messages.turk, "commands": [("Сайт обслуживания", 'https://tm.zgc.su/'), (
        "Как подключить?", 'https://sites.google.com/view/zgcvpn/try?authuser=0')]},
        "/Сотрудничество": {"answer": messages.coop,
                            "commands": [["Сделать предложение", 'https://zgcvpn.ru/partnership']]},
        "/ZGC SHOP": {"answer": messages.shop,
                      "commands": [("ZGC SHOP", 'https://market.zgc.su/'), ("Связаться с поддержкой", '/market')]},
        "/Связаться с поддержкой": {"answer": messages.coop,
                                    "commands": [("Первичная настройка", "/install"), ("Другое", "/other"),
                                                 ('ZGC SHOP', '/market')]},

        "/urgent": {"answer": messages.first_install, "commands": []},
        "/install": {"answer": messages.first_install, "commands": []},
        "/other": {"answer": messages.ru_site_support, "commands": [('.', 'https://market.zgc.su/vpnfaq')]},
        "/market": {"answer": 'Здравствуйте! Укажите, пожалуйста, продукт и вопросы по нему', "commands": []},
        "/rub": {"answer": messages.ru_site_rub_text,
                 "commands": [('Тарифы можно посмотреть тут', 'https://zgcvpn.ru/#tariffs')]},
        "/yuan": {"answer": messages.ru_site_yuan_text, "commands": [('Alipay:', 'https://zgc.su/pay/alipay.jpeg'),
                                                                     ('WeChat pay:', 'https://zgc.su/pay/wechat.png')]},

    }

en_command_answers = {
    "/Payment": {"answer": messages.en_pay_type,
                 "commands": [("In roubles ₽ or in hryvnia ₴", '/rub'), ("In yuan ¥", "/yuan"),
                              ("Connect to support", '/Contact support')]},
    "/Trial period": {"answer": messages.en_site_trial_text,
                      "commands": [('http://zgcvpn.ru', 'http://zgcvpn.ru'), ("Payment", '/Payment'),
                                   ("Contact support", '/Contact support')]},
    "/Learn more": {"answer": "Learn how to block ads, which servers have appeared, and much more",
                    "commands": [["Blog", 'https://market.zgc.su/zgcvpnblog']]},
    "/For Turkmenistan": {"answer": messages.en_turk, "commands": [("Service site", 'https://tm.zgc.su/'), (
    "How to connect?", 'https://sites.google.com/view/zgcvpn/try?authuser=0')]},
    "/Partnership": {"answer": messages.en_coop, "commands": [["Make an offer", 'https://zgcvpn.ru/partnership']]},
    "/ZGC SHOP": {"answer": messages.en_shop,
                  "commands": [("ZGC SHOP", 'https://market.zgc.su/'), ("Contact support", '/market')]},
    "/Contact support": {"answer": messages.en_coop,
                         "commands": [("Initial setup", "/install"), ("Other", "/other"), ('ZGC SHOP', '/market')]},

    "/urgent": {"answer": messages.first_install, "commands": []},
    "/install": {"answer": messages.first_install, "commands": []},
    "/other": {"answer": messages.en_site_support, "commands": [('.', 'https://market.zgc.su/vpnfaq')]},
    "/market": {"answer": 'Hello! Please specify the product and questions about it', "commands": []},
    "/rub": {"answer": messages.en_site_rub_text,
             "commands": [('Rates can be viewed here', 'https://zgcvpn.ru/#tariffs')]},
    "/yuan": {"answer": messages.en_site_yuan_text, "commands": [('Alipay:', 'https://zgc.su/pay/alipay.jpeg'),
                                                                 ('WeChat pay:', 'https://zgc.su/pay/wechat.png')]},
}

command_answers2 = \
    {
        "/Payment": [{"answer": messages.pay_type,
                      "commands": [("В рублях ₽ или в гривнах ₴", '/rub'), ("В юанях ¥", "/yuan"),
                                   ("Связаться с поддержкой", '/Связаться с поддержкой')]}],
        "/Trial period": [{"answer": messages.ru_site_trial_text,
                           "commands": [('http://zgcvpn.ru', 'http://zgcvpn.ru'), ("Оплата", '/Оплата'),
                                        ("Связаться с поддержкой", '/Связаться с поддержкой')]}],
        "/Learn more": [{"answer": "Узнайте как заблокировать рекламу, какие появились сервера и многое другое",
                         "commands": [["Блог", 'https://market.zgc.su/zgcvpnblog']]},
                        {"answer": "также мы есть в телеграме и других соц сетях",
                         "commands": [["Блог", 'https://market.zgc.su/zgcvpnblog']]}],
        "/For Turkmenistan": [{"answer": messages.turk, "commands": [("Сайт обслуживания", 'https://tm.zgc.su/'), (
            "Как подключить?", 'https://sites.google.com/view/zgcvpn/try?authuser=0')]}],
        "/Partnership": [
            {"answer": messages.coop, "commands": [["Сделать предложение", 'https://zgcvpn.ru/partnership']]}],
        "/ZGC SHOP": [{"answer": messages.shop,
                       "commands": [("ZGC SHOP", 'https://market.zgc.su/'), ("Связаться с поддержкой", '/market')]}],
        "/Contact support": [{"answer": messages.coop,
                              "commands": [("Первичная настройка", "/install"), ("Другое", "/other"),
                                           ('ZGC SHOP', '/market')]}],

        "/urgent": [{"answer": messages.first_install, "commands": []}],
        "/install": [{"answer": messages.first_install, "commands": []}],
        "/other": [{"answer": messages.ru_site_support, "commands": [('.', 'https://market.zgc.su/vpnfaq')]}],
        "/market": [{"answer": 'Здравствуйте! Укажите, пожалуйста, продукт и вопросы по нему', "commands": []}],
        "/rub": [
            {
                "answer": 'Пожалуйста, НИЧЕГО НЕ УКАЗЫВАЙТЕ В КОММЕНТАРИЯХ к переводу. Пришлите скриншот оплаты. ',
                "commands": []
            },
            {
                "answer": 'СБЕРБАНК: 5336690228278851',
                "commands": []
            },
            {
                "answer": 'Тинькофф: 5536913846450605',
                "commands": []
            },
            {
                "answer": 'PayPal: vpn@zgc.su',
                "commands": []
            },
            {
                "answer": 'Киви: +79258852363',
                "commands": []
            },
            {
                "answer": 'Яндекс деньги: 410013783404504',
                "commands": [('Тарифы можно посмотреть тут', 'https://zgcvpn.ru/#tariffs')]
            }
        ],
        "/yuan": [{"answer": messages.ru_site_yuan_text, "commands": [('Alipay:', 'https://zgc.su/pay/alipay.jpeg'), (
            'WeChat pay:', 'https://zgc.su/pay/wechat.png')]}],

    }

en_command_answers2 = {
    "/Payment": [{"answer": messages.en_pay_type,
                  "commands": [("In roubles ₽ or in hryvnia ₴", '/rub'), ("In yuan ¥", "/yuan"),
                               ("Connect to support", '/Contact support')]}],
    "/Trial period": [{"answer": messages.en_site_trial_text,
                       "commands": [('http://zgcvpn.ru', 'http://zgcvpn.ru'), ("Payment", '/Payment'),
                                    ("Contact support", '/Contact support')]}],
    "/Learn more": [{"answer": "Learn how to block ads, which servers have appeared, and much more",
                     "commands": [["Blog", 'https://market.zgc.su/zgcvpnblog']]}],
    "/For Turkmenistan": [{"answer": messages.en_turk, "commands": [("Service site", 'https://tm.zgc.su/'), (
        "How to connect?", 'https://sites.google.com/view/zgcvpn/try?authuser=0')]}],
    "/Partnership": [{"answer": messages.en_coop, "commands": [["Make an offer", 'https://zgcvpn.ru/partnership']]}],
    "/ZGC SHOP": [{"answer": messages.en_shop,
                   "commands": [("ZGC SHOP", 'https://market.zgc.su/'), ("Contact support", '/market')]}],
    "/Contact support": [{"answer": messages.en_coop,
                          "commands": [("Initial setup", "/install"), ("Other", "/other"), ('ZGC SHOP', '/market')]}],

    "/urgent": [{"answer": messages.first_install, "commands": []}],
    "/install": [{"answer": messages.first_install, "commands": []}],
    "/other": [{"answer": messages.en_site_support, "commands": [('.', 'https://market.zgc.su/vpnfaq')]}],
    "/market": [{"answer": 'Hello! Please specify the product and questions about it', "commands": []}],
    "/rub": [{"answer": messages.en_site_rub_text,
              "commands": [('Rates can be viewed here', 'https://zgcvpn.ru/#tariffs')]}],
    "/yuan": [{"answer": messages.en_site_yuan_text, "commands": [('Alipay:', 'https://zgc.su/pay/alipay.jpeg'),
                                                                  ('WeChat pay:', 'https://zgc.su/pay/wechat.png')]}],
}

china_command_answers2 = {
    "/Payment": [{"answer": "以卢布或人民币付款？ \n\n如果您对付款有任何其他问题-点击 '联系支持'",
                  "commands": [("陷入困境$或在格里夫纳$", '/rub'), ("在元¥", "/yuan"), ("联系支持", '/Contact support')]}],
    "/Trial period": [{"answer": "要获得免费试用期，请在网站上输入您的电子邮件地址。 这只能做一次。",
                       "commands": [('http://zgcvpn.ru', 'http://zgcvpn.ru'), ("付款", '/Payment'),
                                    ("联系支持", '/Contact support')]}],
    "/Learn more": [{"answer": "了解如何阻止广告，出现了哪些服务器等等", "commands": [["博客", 'https://market.zgc.su/zgcvpnblog']]}],
    "/For Turkmenistan": [{"answer": "要访问土库曼斯坦居民的网站，请点击 服务网站" \
                                     "要获取有关连接的信息，请单击 如何连接？ " \
                                     "在紧急问题的情况下，写信给电子邮件，主题行'TM'vpn@zgc.su", "commands": [("服务站点", 'https://tm.zgc.su/'),
                                                                                         ("如何连接？",
                                                                                          'https://sites.google.com/view/zgcvpn/try?authuser=0')]}],
    "/Partnership": [{"answer": "您可以点击下面的链接描述您的报价", "commands": [["提出报价", 'https://zgcvpn.ru/partnership']]}],
    "/ZGC SHOP": [{"answer": "了解我们的所有产品", "commands": [("ZGC SHOP", 'https://market.zgc.su/'), ("联系支持", '/market')]}],
    "/Contact support": [
        {"answer": "您可以点击下面的链接描述您的报价", "commands": [("初始设置", "/install"), ("其他", "/other"), ('ZGC SHOP', '/market')]}],

    "/urgent": [{"answer": messages.first_install, "commands": []}],
    "/install": [{"answer": messages.first_install, "commands": []}],
    "/other": [{"answer": messages.en_site_support, "commands": [('.', 'https://zgcvpn.ru/faq')]}],
    "/market": [{"answer": '你好！ 请指定产品和有关它的问题', "commands": []}],
    "/rub": [{"answer": messages.en_site_rub_text,
              "commands": [('Rates can be viewed here', 'https://zgcvpn.ru/#tariffs')]}],
    "/yuan": [{"answer": messages.en_site_yuan_text, "commands": [('Alipay:', 'https://zgc.su/pay/alipay.jpeg'),
                                                                  ('WeChat pay:', 'https://zgc.su/pay/wechat.png')]}],

    "/chinese": [
        {"answer": "亲亲，欢迎光临 ZGC VPN。 请注意地读。", "commands": []},
        {"answer": "我们从 17:00 到 22:00 工作，如果您不等待答复，我们将通过邮件发送。如需人工客服，请在17:00 - 22:00期间来访，到时发送问题即可。", "commands": []},
        {"answer": "如果您是客户并希望续订服务，请查看您的电子邮件。 我们已向您发送付款二维码。 付款后请截图发给我们。PayPal: vpn@zgc.su 发给我图片，然后耐心等待email", "commands": []},

    ]
}

# после такой команты открывается еще и диалог с тех поддержкой
open_dialog_cmds = ["/market"]

viewed_cmds = ["/Оплата", "/Пробный период", "/Узнать больше", "/Для Туркменистана", "/Сотрудничество", "/ZGC SHOP",
               "/Связаться с поддержкой"]

ws_email_wsClient = {}


def send_ws_msg(client_email, message):
    ws = ws_email_wsClient[client_email]

    return ws.send(message)


def add_ws_conn(email, ws):
    ws_email_wsClient[email] = ws
    # insert code for add pin client
    print('added ws for - ' + email)


def remove_ws_conn(email):
    import helpers

    del ws_email_wsClient[email]
    helpers.send_msg_to_tg("email: " + email + "\n клиент покинул чат")
    # insert code for unpin client


callback_cmd_list = ['/urgent', '/install', '/other', '/market', '/rub', '/yuan', '/sup', '/pay']

all_commands = command_answers.keys()
# print(all_commands)
