from threading import Event, Thread

from blinker_app import consts
from blinker_app.digital_boards import BaseBuzzerBoard, BaseLedBoard
from blinker_app.mqtt_utils import client, subscribers

if __name__ == "__main__":
    led_event: Event = Event()
    buzzer_event: Event = Event()

    led_board: BaseLedBoard = BaseLedBoard(3, 2, 6)
    led_board_thread: Thread = Thread(target=led_board.run, args=(led_event,), daemon=True)

    buzzer_board: BaseBuzzerBoard = BaseBuzzerBoard(5)
    buzzer_board_thread: Thread = Thread(target=buzzer_board.run, args=(buzzer_event,), daemon=True)

    subscriber: subscribers.BaseSubscriber = subscribers.BaseSubscriber(client.Client().instance)
    subscriber_thread: Thread = Thread(
        target=subscriber.subscribe,
        args=(
            {
                consts.ZoneTopicType.ACTIVATION.value: led_event,
                consts.ZoneTopicType.CONFIRMATION.value: buzzer_event,
            },
        ),
        daemon=True,
    )

    led_board_thread.start()
    buzzer_board_thread.start()
    subscriber_thread.start()

    led_board_thread.join()
    buzzer_board_thread.join()
    subscriber_thread.join()
