from threading import Event
from typing import Any

from paho.mqtt import client as mqtt_client
from paho.mqtt.client import MQTTMessageInfo


class BaseSubscriber:
    def __init__(self, client_instance: mqtt_client.Client) -> None:
        self._client_instance: mqtt_client.Client = client_instance

    @staticmethod
    def _on_message(event: Event):
        def on_message(client_instance: mqtt_client.Client, userdata: Any, msg: MQTTMessageInfo) -> None:
            match msg.payload.decode():
                case "1":
                    event.set()
                case "0":
                    event.clear()
                case _:
                    print("Not handled")

        return on_message

    def subscribe(self, topic: str, event: Event) -> None:
        self._client_instance.subscribe(topic)
        self._client_instance.on_message = self._on_message(event)
        self._client_instance.loop_forever()
