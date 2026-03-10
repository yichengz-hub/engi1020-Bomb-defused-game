from morse_code import *
from timer_module import *
from simon_says import *
import asyncio

win = 0

timer = Timer((1,1,1))
morse_code = Morsecode(8, 9, 7)
morse_code.start()
simon_says = SimonSays()

async def loop():
    global morse_code, win, strikes, timer

    while timer.current_strikes <= 3:

        timer_task = asyncio.create_task(timer.strikes())
        morse_task = asyncio.create_task(morse_code.main())
        morsecode_result = await morse_task

        if morsecode_result == "code lose":
            await timer.add_strike()
        else:
            win += 1

        if strikes > 0:
            await timer.strikes()

        timer_task.cancel()
        try:
            await timer_task
        except asyncio.CancelledError:
            pass
        morse_task.cancel()

asyncio.run(loop())