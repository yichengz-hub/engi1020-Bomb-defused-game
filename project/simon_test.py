from simon_says import *
print('test')

async def test():
    oled_clear()
    round = 0
    strikes = 0
    colour_sequence = []
    first_time = True
    simon_test = SimonSays(5, 5, 3, 9, 10, 11, 12, 13, 4)

    while strikes < 3: 
        simon_test.start(initial_round=round, initial_strikes=strikes, initial_colours=colour_sequence)
        if first_time:
            await simon_test.increase_round() 
            first_time = False    
        simon_task = asyncio.create_task(simon_test.play())

        while True:
            if simon_task.done():
                results = await simon_task

                if results == 'WIN':
                    print(results)
                    return results
                
                elif results == 'Lose':
                    print(results)
                    return results
                
                round, strikes, colour_sequence = results
                break
            await asyncio.sleep(0.1)

asyncio.run(test())