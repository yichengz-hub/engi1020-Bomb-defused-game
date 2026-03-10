from morse_code import *
from timer_module import *
import asyncio

strike = 0
win = 0

timer = Timer((4))
morse_code = Morsecode(8, 9, 7)
morse_code.start()

async def game():
    global morse_code, win, strike, timer
    
    timer_task = asyncio.create_task(timer.strikes())

    morse_task = asyncio.create_task(morse_code.main())
    morsecode_result = await morse_task

    if morsecode_result == "code lose":
        strike += 1
        await timer.add_strike()
    else:
        win += 1

    if strike > 0:
        await timer.strikes()

    timer_task.cancel()
    try:
        await timer_task
    except asyncio.CancelledError:
        pass
    morse_task.cancel()

asyncio.run(game())