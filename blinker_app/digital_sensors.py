from __future__ import annotations

from typing import Any, Unpack

from grovepi import digitalWrite, pinMode


class BaseDigitalSensor:
    __instances: dict[int, BaseDigitalSensor] = {}

    def __new__(cls, **kwargs: Unpack[dict[str, Any]]) -> BaseDigitalSensor:
        pin: int = kwargs["pin"]
        if not (instance := cls.__instances.get(pin)):
            instance: BaseDigitalSensor = super().__new__(cls)
            instance.__is_initialized = False
            cls.__instances[pin] = instance
        return instance

    def __init__(self, *, pin: int) -> None:
        if not self.__is_initialized:
            self._pin: int = pin
            self._is_on: bool = False
            pinMode(pin, "OUTPUT")
            self.__is_initialized = True

    def on(self) -> None:
        digitalWrite(self._pin, 1)
        self._is_on = True

    def off(self) -> None:
        digitalWrite(self._pin, 0)
        self._is_on = False

    @property
    def is_on(self) -> bool:
        return self._is_on
