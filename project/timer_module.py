from engi1020.arduino.api import *
import asyncio
import tm1637
import time


class Timer:
    def __init__(self, clk, dio, led_pins: tuple):
        self.display = tm1637.TM1637(clk=clk, dio=dio)

        self.strike_leds = led_pins
        self.current_strikes = 0
        self.time_left = 300   # 5 minutes
        self._lock = asyncio.Lock()

    async def run_countdown(self):
        while self.time_left >= 0:

            # Convert seconds to MMSS
            minutes = self.time_left // 60
            seconds = self.time_left % 60
            display_value = minutes * 100 + seconds

            # Example: 4:59 -> 0459
            self.display.write(display_value)

            if self.time_left == 0:
                print("KABOOM!")
                return

            await asyncio.sleep(1)
            self.time_left -= 1

    async def strike_monitor(self):
        while True:
            async with self._lock:
                for i, pin in enumerate(self.strike_leds):
                    digital_write(pin, i < self.current_strikes)

            await asyncio.sleep(0.1)

    async def add_strike(self):
        async with self._lock:
            if self.current_strikes < len(self.strike_leds):
                self.current_strikes += 1
                print(f"STRIKE! Total strikes: {self.current_strikes}")


async def main():
    RELAY_POWER_PIN = 7
    STRIKE_LEDS = (10, 11)

    print("Powering up timer module...")
    digital_write(RELAY_POWER_PIN, True)
    time.sleep(0.5)

    bomb_timer = Timer(clk=3, dio=2, led_pins=STRIKE_LEDS)

    print("Starting Bomb Timer and Strike Monitor...")

    await asyncio.gather(
        bomb_timer.run_countdown(),
        bomb_timer.strike_monitor()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nBomb Defused (Program Stopped).")
        digital_write(7, False)
