from simon_says import *
import asyncio
from engi1020.arduino.api import *

async def test():
    simon_test = SimonSays(5, 5, 3, 9, 10, 11, 12, 13, 4)
    simon_test.start()

    await simon_test.increase_round()
    oled_clear()
    await simon_test.play()

asyncio.run(test())