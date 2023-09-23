import sqlite3 as sql
import config
from flask import Flask, request, send_from_directory, redirect
import data_structs as ds
from helpers import bot, autopay
import json

app = Flask(__name__)
url_prefix = ""


def db_find_value(col_name, value):
    """ Check if value exists in database and return corresponding row, 'col_name' must be name of DB column
        DB columns in order: email, date, tariff, sub, tg_id, vk_id, fb_id, state, rate, review_time, received, verified """

    with sql.connect(config.db_file) as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM clients WHERE " + col_name + " = ?", (str(value).lower(),))
        res = cur.fetchall()

        if res:
            return res[0]

        return 0


# --------------------------------------------------
def client_info_msg(col_name, value):
    """ Make a message with client tariff info """

    info = db_find_value(col_name, value)
    if not info:
        return "No info about client"

    message = f"\U00002139\nemail: {info[0]}\n" \
              f"date: {info[1]}\n" \
              f"tariff: {info[2]}\n" \
              f"sub: {info[3]}\n"

    return message


@app.route('/')
def hello2():
    return redirect(url_prefix + "/static/chat_app/chat.html", code=302)


@app.route(url_prefix + '/')
def hello():
    return redirect(url_prefix + "/static/chat_app/chat.html", code=302)


def send_img_to_tg(name, email):
    message = client_info_msg("email", email) + "\nWeb_client"

    with open("static/web_files/" + name, 'rb') as f:
        bot.send_photo(chat_id=config.group_id, photo=f, caption=message)


@app.route(url_prefix + "/email", methods=['POST'])
def email():
    client_email = request.json['email'].lower()

    if client_info_msg('email', client_email) == 'No info about client':
        client = [client_email, "-", "-", "-", "0", "0", "0", "CLOSED", "0", "0", "NO", 0, 0, 0]
        with sql.connect(config.db_file) as con:
            cur = con.cursor()
            cur.execute(f"INSERT INTO clients VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", client)

            return {"status": "created new row"}

    return {"status": "already exists"}


@app.route(url_prefix + '/photo', methods=['POST'])
def photo():
    file = request.files['file']
    email = request.form['user'].lower()

    file.save("static/web_files/" + file.filename)

    send_img_to_tg(file.filename, email)
    if request.form['client_state'] == 'pay':
        if autopay(email, 'email', "static/web_files/" + file.filename):
            import data_structs as ds
            import asyncio

            ws_message = json.dumps({'from': 'bot',
                                     'message': "Спасибо за оплату.\nПодписка отправлена вам на почту вместе с инструкциями. "})
            asyncio.run(ds.send_ws_msg(email, ws_message))
            ws_message = json.dumps({'from': 'bot', 'message': """Попробуйте связываться с нами в социальных сетях, это удобно:
            VK: vk.com/ZhongGuoCu 
            Telegeram: t.me/ZGC_VPN_BOT"""})
            asyncio.run(ds.send_ws_msg(email, ws_message))

    return {"status": "ok", "url": url_prefix + "/static/web_files/" + file.filename}


@app.route(url_prefix + '/support/message', methods=['POST'])
def support_message():
    email = request.json['email'].lower()
    message = request.json['message']

    message_data = "💬\n " + message + "\n\n" + client_info_msg("email", email) + "\nWeb_client"

    # print(message_data)

    bot.send_message(config.group_id, message_data)

    return {'status': 'ok'}


@app.route(url_prefix + '/chat', methods=['POST', 'GET'])
def chat_message():
    meth = request.method

    command = request.json['message']
    lang = 'ru'

    try:
        lang = request.json['language']
    except Exception:
        print('not defined key - language')

    answer = {}

    commands = []
    if lang == 'en':
        commands = ds.en_command_answers2
    elif lang == 'ch':
        commands = ds.china_command_answers2
    else:
        commands = ds.command_answers2

    if (command in commands.keys()):
        answer = {"messages": commands[command]}
    else:
        answer = {"messages": [{"answer": "unknown command", "commands": []}]}

    return answer


@app.route(url_prefix + '/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


@app.route(url_prefix + '/commands')
def all_commands():
    answer = {'data': list(ds.viewed_cmds)}
    return answer


def serve(app, host, port):
    app.run(host=host, port=port, ssl_context='adhoc')


def main():
    print('starting server')
    serve(app, '127.0.0.1', 5443)
