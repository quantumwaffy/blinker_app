from threading import Event, Thread

from blinker_app.digital_boards import BaseBuzzerBoard, BaseLedBoard
from blinker_app.mqtt_utils import client, subscribers

if __name__ == "__main__":
    led_event: Event = Event()
    buzzer_event: Event = Event()

    subscriber: subscribers.BaseSubscriber = subscribers.BaseSubscriber(client.Client().instance)

    led_board: BaseLedBoard = BaseLedBoard(3, 2, 6)
    led_board_thread: Thread = Thread(target=led_board.run, args=(led_event,), daemon=True)

    buzzer_board: BaseBuzzerBoard = BaseBuzzerBoard(5)
    buzzer_board_thread: Thread = Thread(target=buzzer_board.run, args=(buzzer_event,), daemon=True)

    activation_subscriber_thread: Thread = Thread(
        target=subscriber.subscribe, args=("zone/activation", led_event), daemon=True
    )
    confirmation_subscriber_thread: Thread = Thread(
        target=subscriber.subscribe, args=("zone/confirmation", buzzer_event), daemon=True
    )

    led_board_thread.start()
    buzzer_board_thread.start()
    activation_subscriber_thread.start()
    confirmation_subscriber_thread.start()

    led_board_thread.join()
    buzzer_board_thread.join()
    activation_subscriber_thread.join()
    confirmation_subscriber_thread.join()
