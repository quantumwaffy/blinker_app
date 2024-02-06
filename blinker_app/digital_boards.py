from __future__ import annotations

import abc
import itertools
import time
from threading import Event
from types import TracebackType
from typing import Any, Unpack

from blinker_app.digital_sensors import BaseDigitalSensor


class BaseDigitalBoard(abc.ABC):
    __instances: dict[tuple[int, ...], BaseDigitalBoard] = {}

    def __new__(cls, *args: Unpack[tuple[int, ...]]) -> BaseDigitalBoard:
        pins: tuple[int, ...] = tuple(sorted(args))

        if instance := cls.__instances.get(pins):
            return instance

        used_pins: set[int] = set(itertools.chain.from_iterable(cls.__instances.keys()))
        if any(pin in used_pins for pin in pins):
            raise RuntimeError(f"Cannot create the board. Pins '{used_pins}' are already in use")

        instance: BaseDigitalBoard = super().__new__(cls)
        instance.__is_initialized = False
        cls.__instances[pins] = instance
        return instance

    def __init__(self, *pins: Unpack[tuple[int, ...]]) -> None:
        if not self.__is_initialized:
            if not pins:
                raise RuntimeError("Cannot create the board without connected digital sensors")
            self._sensors: dict[str, BaseDigitalSensor] = {
                f"{self._sensor_name_prefix}{pin}": BaseDigitalSensor(pin=pin) for pin in pins
            }
            time.sleep(1)
            self.__is_initialized = True

    def __getattr__(self, item: str) -> Any:
        if value := self._sensors.get(item):
            return value
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

    def _off_sensors(self) -> None:
        [sensor.off() for sensor in self._sensors.values() if sensor.is_on]

    def __enter__(self) -> BaseDigitalBoard:
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, traceback: TracebackType | None
    ) -> bool | None:
        self._off_sensors()

    @property
    @abc.abstractmethod
    def _sensor_name_prefix(self) -> str:
        ...

    @abc.abstractmethod
    def run(self, event: Event) -> None:
        ...


class BaseLedBoard(BaseDigitalBoard):
    _sensor_name_prefix = "led_"

    def run(self, event: Event) -> None:
        if len(self._sensors) < 2:
            raise RuntimeError("Provide 2 or more leds or override base blinking logic in the 'run' method")
        first, *middles, last = self._sensors.values()
        while event.wait():
            first.on()
            last.on()
            time.sleep(2)
            first.off()
            last.off()
            [middle_led.on() for middle_led in middles]
            time.sleep(2)
            [middle_led.off() for middle_led in middles]


class BaseBuzzerBoard(BaseDigitalBoard):
    _sensor_name_prefix = "buzzer_"

    def run(self, event: Event) -> None:
        one_buzzer: BaseDigitalSensor = self._sensors.copy().popitem()[-1]
        while event.wait():
            one_buzzer.on()
            time.sleep(1)
            one_buzzer.off()
            time.sleep(1)
