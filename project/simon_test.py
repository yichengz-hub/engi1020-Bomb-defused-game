from simon_says import *
import asyncio
from engi1020.arduino.api import *

async def test():
    simon_test = SimonSays(5, 5, 1, 2, 3, 4, 6, 7, 8)
    simon_test.start()

    while True:  
        await simon_test.increase_round()
        await simon_test.play()
        oled_clear()

        if simon_test.current_round >= simon_test.round_number:
            print("Game done")
            break

        await asyncio.sleep(0.1)

asyncio.run(test())