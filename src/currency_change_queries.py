import sqlite3 as sql
import config


def check_user(tg_id=None, vk_id=None):
    if tg_id is not None:
        search_col = "tg_id"
        search_val = tg_id
    else:
        search_col = "vk_id"
        search_val = vk_id

    with sql.connect(config.db_file) as con:
        cur = con.cursor()
        cur.execute(f"SELECT wechat_number FROM currencies_clients WHERE {search_col} = '{search_val}';")
        info = cur.fetchall()
    if info:
        return info[0][0]
    return None


def add_user(wechat_number, tg_id="", vk_id=""):
    with sql.connect(config.db_file) as con:
        cur = con.cursor()
        cur.execute(f"INSERT INTO currencies_clients (tg_id,vk_id,wechat_number) "
                    f"VALUES ('{tg_id}', '{vk_id}', '{wechat_number}');")


def Salter_table(query):
    with sql.connect(config.db_file) as con:
        cur = con.cursor()
        q = query[8:]
        try:
            a = cur.execute(q)
        except Exception as e:
            return e.args
        return a


def update_wechat(message):
    _, tg_id, new_wechat = message.lower().split()
    with sql.connect(config.db_file) as con:
        cur = con.cursor()
        cur.execute(f"UPDATE currencies_clients "
                    f"SET wechat_number = {new_wechat} "
                    f"WHERE tg_id = {tg_id};")
