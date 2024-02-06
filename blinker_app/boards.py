from __future__ import annotations

import itertools
import time
from threading import Event
from types import TracebackType
from typing import Any, Unpack

from blinker_app.leds import Led


class BaseBoard:
    __instances: dict[tuple[int, ...], BaseBoard] = {}
    _led_name_prefix: str = "led_"

    def __new__(cls, *args: Unpack[tuple[int, ...]]) -> BaseBoard:
        pins: tuple[int, ...] = tuple(sorted(args))

        if instance := cls.__instances.get(pins):
            return instance

        used_pins: set[int] = set(itertools.chain.from_iterable(cls.__instances.keys()))
        if any(pin in used_pins for pin in pins):
            raise RuntimeError(f"Cannot create the board. Pins '{used_pins}' are already in use")

        instance: BaseBoard = super().__new__(cls)
        instance.__is_initialized = False
        cls.__instances[pins] = instance
        return instance

    def __init__(self, *pins: Unpack[tuple[int, ...]]) -> None:
        if not self.__is_initialized:
            if not pins:
                raise RuntimeError("Cannot create the board without connected leds")
            self._leds: dict[str, Led] = {f"{self._led_name_prefix}{pin}": Led(pin=pin) for pin in pins}
            time.sleep(1)
            self.__is_initialized = True

    def __getattr__(self, item: str) -> Any:
        if value := self._leds.get(item):
            return value
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

    def _off_leds(self) -> None:
        [led.off() for led in self._leds.values() if led.is_on]

    def __enter__(self) -> BaseBoard:
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, traceback: TracebackType | None
    ) -> bool | None:
        self._off_leds()

    def run(self, event: Event) -> None:
        if len(self._leds) < 2:
            raise RuntimeError("Provide 2 or more leds or override base blinking logic in the 'run' method")
        first, *middles, last = self._leds.values()
        while event.wait():
            first.on()
            last.on()
            time.sleep(2)
            first.off()
            last.off()
            [middle_led.on() for middle_led in middles]
            time.sleep(2)
            [middle_led.off() for middle_led in middles]
