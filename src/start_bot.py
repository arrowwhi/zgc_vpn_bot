import threading
import telegram as tg
import vkontakte as vk
# import facebook as fb
import ws_chat_server as ws_server
from src import chat_server as chat, database as db

t1 = threading.Thread(target=tg.main)
t2 = threading.Thread(target=vk.main)
# t3 = threading.Thread(target=fb.main)
t4 = threading.Thread(target=db.main)
t5 = threading.Thread(target=chat.main)
t6 = threading.Thread(target=ws_server.start_ws_server)

t1.start()
t2.start()
# t3.start()
t4.start()
t5.start()
t6.start()
