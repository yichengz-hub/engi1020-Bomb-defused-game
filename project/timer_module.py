from engi1020.arduino.api import *
import asyncio

class Timer():
    def __init__(self, led_pins: tuple):
        self.strike_leds = led_pins
        self.current_strikes = 0
        self._lock = asyncio.Lock()

    async def strikes(self):
        while True:
            async with self._lock:
                for i in range(len(self.strike_leds)):
                    pin = self.strike_leds[i]
                    if i < self.current_strikes: 
                        digital_write(pin, True)
                    else:
                        digital_write(pin, False)
            await asyncio.sleep(0.1)

    async def add_strike(self):
        async with self._lock:
            self.current_strikes += 1
