from threading import Event, Thread

from blinker_app.boards import BaseBoard
from blinker_app.mqtt_utils import client, subscribers

if __name__ == "__main__":
    event: Event = Event()
    subscriber: subscribers.BaseSubscriber = subscribers.BaseSubscriber(client.Client().instance)
    board: BaseBoard = BaseBoard(3, 2, 6)

    board_thread: Thread = Thread(target=board.run, args=(event,), daemon=True)
    subscriber_thread: Thread = Thread(target=subscriber.subscribe, args=("zone/activation", event), daemon=True)

    board_thread.start()
    subscriber_thread.start()

    board_thread.join()
    subscriber_thread.join()
