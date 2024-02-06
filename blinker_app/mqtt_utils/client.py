import random
import time
from typing import Any

from paho.mqtt import client as mqtt_client


class Client:
    def __init__(
        self,
        client_id: str | None = None,
        broker_url: str = "broker.emqx.io",
        broker_port: int = 1883,
        first_reconnect_delay: int = 1,
        reconnect_rate: int = 2,
        max_reconnect_count: int = 12,
        max_reconnect_delay: int = 60,
        use_tls: bool = False,
    ) -> None:
        self._client_id: str = client_id or f"python-mqtt-{random.randint(0, 1000)}"
        self._broker_url: str = broker_url
        self._broker_port: int = broker_port
        self._first_reconnect_delay: int = first_reconnect_delay
        self._reconnect_rate: int = reconnect_rate
        self._max_reconnect_count: int = max_reconnect_count
        self._max_reconnect_delay: int = max_reconnect_delay
        self._use_tls: bool = use_tls

        self.instance: mqtt_client.Client = self._get_instance()

    @staticmethod
    def _on_connect(client: mqtt_client.Client, userdata: Any, flags: Any, rc: int) -> None:
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code: {rc}")

    def _on_disconnect(self):
        def on_disconnect(client: mqtt_client.Client, userdata: Any, rc: int):
            print(f"Disconnected with result code: {rc}")
            reconnect_count, reconnect_delay = 0, self._first_reconnect_delay
            while reconnect_count < self._max_reconnect_count:
                print(f"Reconnecting in {reconnect_delay} seconds...")
                time.sleep(reconnect_delay)

                try:
                    client.reconnect()
                    print("Reconnected successfully!")
                    return
                except Exception as err:
                    print(f"{err}. Reconnect failed. Retrying...", err)

                reconnect_delay *= self._reconnect_rate
                reconnect_delay = min(reconnect_delay, self._max_reconnect_delay)
                reconnect_count += 1
            print(f"Reconnect failed after {reconnect_count} attempts. Exiting...")

        return on_disconnect

    def _get_instance(self) -> mqtt_client.Client:
        instance: mqtt_client.Client = mqtt_client.Client(self._client_id)
        instance.on_connect = self._on_connect
        instance.on_disconnect = self._on_disconnect()

        if self._use_tls:
            instance.tls_set(ca_certs="cert.crt")

        instance.connect(self._broker_url, self._broker_port)
        return instance
