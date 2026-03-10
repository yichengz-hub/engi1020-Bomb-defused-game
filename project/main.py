from morse_code import *
from timer_module import *
from simon_says import *
import asyncio

win = 0

timer = Timer((1,1,1))
morse_code = Morsecode(8, 9, 7)
morse_code.start()
simon_says = SimonSays(5,1,1,1,1,1,1,1,1)
simon_says.start()
simon_says.increase_round()

async def loop():
    global morse_code, win, strikes, timer

    simon_task = asyncio.create_task(simon_says.play())
    timer_task = asyncio.create_task(timer.strikes())
    morse_task = asyncio.create_task(morse_code.main())

    while timer.current_strikes <= 3:
        
        if simon_task.done():
            simon_result = await simon_task
            if simon_result == False:
                await timer.add_strike()
                simon_task = asyncio.create_task(simon_says.play())
            elif simon_result == True:
               simon_says.increase_round()
               simon_task = asyncio.create_task(simon_says.play())
               if len(simon_says.colour_sequence) >= simon_says.rounds:
                   # TODO If the above condition is satisfied you have won simon says,
                   # TODO light up the led and such...
                   pass

        if morse_task.done():
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