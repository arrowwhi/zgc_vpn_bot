import asyncio
import json

import websockets

from src import data_structs as ds


async def hello(websocket, path):
    print(path)
    name = await websocket.recv()
    print(f"< {name}")

    greeting = f"Hello {name}!"

    await websocket.send(greeting)
    print(f"> {greeting}")


async def initWsConn(ws, path):
    print('new ws conn')
    ws_msg = await ws.recv()
    msg = json.loads(ws_msg)
    email = msg['email'].lower()

    ds.add_ws_conn(email, ws)
    print('added ws conn')

    message = json.dumps({'type': 'cmd', 'message': 'connected succsessfully'})
    await ds.send_ws_msg(email, message)

    while True:
        try:
            await ds.send_ws_msg(email, json.dumps({'type': 'ping'}))
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected.  Do cleanup")
            ds.remove_ws_conn(email)
            break
        await asyncio.sleep(15)


def start_ws_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    start_server = websockets.serve(initWsConn, "0.0.0.0", 5500)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

    print('ws server stopped')

