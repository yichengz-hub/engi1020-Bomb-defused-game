from engi1020.arduino.api import *
import asyncio
from random import choice
from time import time

class SimonSays:
    def __init__(self, total_rounds,  buzzer_pin, r_button, y_button, b_button, g_button, r_led, g_led, b_led):
        self.total_rounds = total_rounds
        self.buzzer_pin = buzzer_pin
        self.r_button = r_button
        self.y_button = y_button
        self.b_button = b_button
        self.g_button = g_button
        self.r_led = r_led
        self.g_led = g_led
        self.b_led = b_led


    def start(self, initial_round=0, initial_strikes=0, initial_colours=[], max_strikes=3):
        self.r_frequency = 550
        self.y_frequency = 622
        self.b_frequency = 830
        self.g_frequency = 1000
        self.colour_time = 0.8
        self.next_round = False
        self.current_round = initial_round
        self.strikes = initial_strikes
        self.game_loose_time = 1.5
        self.strike_time = 0.2
        self.strike_frequency = 100
        self.colour_sequence = initial_colours
        self.max_strikes = max_strikes
        self.colours = ['red', 'blue', 'yellow', 'green']

        self.mapping = {
            0: {'red': 'blue', 'blue': 'red', 'green': 'yellow', 'yellow': 'green' },
            1: {'red': 'yellow', 'blue': 'green', 'green': 'blue', 'yellow': 'red' }, 
            2: {'red': 'green', 'blue': 'red', 'green': 'yellow', 'yellow': 'blue' },
        }

        self.matching_colours = [self.mapping[self.strikes][colour] for colour in self.colours]
        self.input_colour_sequence = [self.mapping[self.strikes][color] for color in self.colour_sequence]

        print(self.matching_colours)


    async def wait_for_release(self):
        # Wait until ALL buttons are released
        while (
            digital_read(self.r_button) or
            digital_read(self.b_button) or
            digital_read(self.y_button) or
            digital_read(self.g_button)
        ):
            await asyncio.sleep(0.02)

        # Extra debounce / settle delay
        await asyncio.sleep(0.15)

        print("[SIMON] Buttons fully released and settled")


    async def win_sound(self):
        notes = [523, 659, 784, 1047]
        for note in notes:
            buzzer_note(self.buzzer_pin, note, 0.15)
            await asyncio.sleep(0.15)


    async def lose_sound(self):
        notes = [784, 659, 523, 392]
        for note in notes:
            buzzer_note(self.buzzer_pin, note, 0.15)
            await asyncio.sleep(0.25)



    async def increase_round(self):
        index = choice(range(len(self.colours)))
        self.colour_sequence.append(self.colours[index])
        self.input_colour_sequence.append(self.matching_colours[index])
        self.current_round += 1
        await asyncio.sleep(0.05)


    async def play(self):
        if self.total_rounds <= 0:
            print("0 or less rounds selected -> auto win")
            await self.win_sound()
            return "WIN"
        while True:     
            if self.strikes >= self.max_strikes:
                print("You lose the game!")
                await self.lose_sound()
                await asyncio.sleep(0.2)
                return 'LOSE'

            # Check if the round needs to be increased, if it does, add a random colour to the sequence.
            if self.next_round == True:
                await self.increase_round()
                self.next_round = False
            
            for colour in self.colour_sequence:
                if colour == 'red':
                    print(colour)
                    digital_write(self.r_led, True)
                    buzzer_note(self.buzzer_pin, self.r_frequency, self.colour_time)
                    await asyncio.sleep(self.colour_time)
                    digital_write(self.r_led, False)
                elif colour == 'blue':
                    print(colour)
                    digital_write(self.b_led, True)
                    buzzer_note(self.buzzer_pin, self.b_frequency, self.colour_time)
                    await asyncio.sleep(self.colour_time)
                    digital_write(self.b_led, False)
                elif colour == 'yellow':
                    print(colour)
                    digital_write(self.r_led, True)
                    digital_write(self.g_led, True)
                    buzzer_note(self.buzzer_pin, self.y_frequency, self.colour_time)
                    await asyncio.sleep(self.colour_time)
                    digital_write(self.g_led, False)
                    digital_write(self.r_led, False)
                else:
                    print(colour)
                    digital_write(self.g_led, True)
                    buzzer_note(self.buzzer_pin, self.g_frequency, self.colour_time)
                    await asyncio.sleep(self.colour_time)
                    digital_write(self.g_led, False)


            # This loop runs after the colours have been played.
            # It checks for user input and if there is no input for 2 seconds, the colours play again.
            start_time = time()
            while True:
                print("waiting for input...")
                r_input = digital_read(self.r_button)
                b_input = digital_read(self.b_button)
                y_input = digital_read(self.y_button)
                g_input = digital_read(self.g_button)

                # If the user inputs a colour, we then take the future inputs and check if it is the correct sequence.
                if r_input == True:
                    first_input = 'red'
                    print("red inputted")
                    digital_write(self.r_led, True)
                    buzzer_note(self.buzzer_pin, self.r_frequency, self.colour_time)
                    await asyncio.sleep(self.colour_time)
                    digital_write(self.r_led, False)
                    await self.wait_for_release()
                    break
                elif b_input == True:
                    first_input = 'blue'
                    print("blue inputted")
                    digital_write(self.b_led, True)
                    buzzer_note(self.buzzer_pin, self.b_frequency, self.colour_time)
                    await asyncio.sleep(self.colour_time)
                    digital_write(self.b_led, False)
                    await self.wait_for_release() 
                    break
                elif y_input == True:
                    first_input = 'yellow'
                    print("yellow inputted")
                    digital_write(self.r_led, True)
                    digital_write(self.g_led, True)
                    buzzer_note(self.buzzer_pin, self.y_frequency, self.colour_time)
                    await asyncio.sleep(self.colour_time)
                    digital_write(self.r_led, False)
                    digital_write(self.g_led, False)
                    await self.wait_for_release()
                    break
                elif g_input == True:   
                    first_input = 'green'
                    print("green inputted")
                    digital_write(self.g_led, True)
                    buzzer_note(self.buzzer_pin, self.g_frequency,  self.colour_time)
                    await asyncio.sleep(self.colour_time)
                    digital_write(self.g_led, False)
                    await self.wait_for_release()
                    break
                
                # If nothing is inputted for 2 seconds, the colours begin to play again.
                if time() - start_time > 2:
                    print("Time's up! The colours will play again.")
                    first_input = 'timeout'
                    break

                await asyncio.sleep(0.01)
            

            # The user has entered an input, start the sequence of checking the next inputs
            if first_input != 'timeout':

                start_time = time()
                inputted_sequence = [first_input]
                input_count = 0

                print("\nwaiting for future inputs...")

                await asyncio.sleep(0.2)

                while True:
                    # If an element of the inputted sequence is not the same as the colour sequence for the same index,
                    # Then the user gets a strike and the colours play again.
                    if not inputted_sequence[input_count] == self.input_colour_sequence[input_count]:
                        self.strikes += 1
                        print(f"You got a strike, total number is: {self.strikes}")
                        await self.lose_sound()
                        await asyncio.sleep(0.2)
                        return self.current_round, self.strikes, self.colour_sequence
                    
                    # If the inputted sequence is exactly the same as the colour sequence,
                    # then the user wins the round and we increase the round number by 1.  
                    elif inputted_sequence == self.input_colour_sequence:
                        self.next_round = True
                        print("Round complete!")
                        if self.current_round >= self.total_rounds:
                            print("You win the game!")
                            await self.win_sound()
                            return "WIN"
                        break

                    r_input = digital_read(self.r_button)
                    b_input = digital_read(self.b_button)
                    y_input = digital_read(self.y_button)
                    g_input = digital_read(self.g_button)

                    if r_input == True:
                        inputted_sequence.append('red')
                        print("red inputted")
                        input_count += 1
                        start_time = time()  
                        digital_write(self.r_led, True)
                        buzzer_note(self.buzzer_pin, self.r_frequency, self.colour_time)
                        await asyncio.sleep(self.colour_time)
                        digital_write(self.r_led, False)
                        await self.wait_for_release()
                    elif b_input == True:
                        inputted_sequence.append('blue')
                        print("blue inputted")
                        input_count += 1
                        start_time = time()
                        digital_write(self.b_led, True)
                        buzzer_note(self.buzzer_pin, self.b_frequency, self.colour_time)
                        await asyncio.sleep(self.colour_time)
                        digital_write(self.b_led, False)
                        await self.wait_for_release()
                    elif y_input == True:
                        inputted_sequence.append('yellow')
                        print("yellow inputted")
                        input_count += 1
                        start_time = time()
                        digital_write(self.r_led, True)
                        digital_write(self.g_led, True)
                        buzzer_note(self.buzzer_pin, self.y_frequency, self.colour_time)
                        await asyncio.sleep(self.colour_time)
                        digital_write(self.r_led, False)
                        digital_write(self.g_led, False)
                        await self.wait_for_release()
                    elif g_input == True:
                        inputted_sequence.append('green')
                        print("green inputted")
                        input_count += 1
                        start_time = time()
                        digital_write(self.g_led, True)
                        buzzer_note(self.buzzer_pin, self.g_frequency, self.colour_time)
                        await asyncio.sleep(self.colour_time)
                        digital_write(self.g_led, False)
                        await self.wait_for_release()

                    if time() - start_time > 2:
                        # you get a strike if the above condition is true
                        self.strikes += 1
                        print(f"You got a strike, total number is: {self.strikes}")
                        await self.lose_sound()
                        await asyncio.sleep(0.2)
                        return self.current_round, self.strikes, self.colour_sequence
                    
                    await asyncio.sleep(0.01)


if __name__ == '__main__':
    print('test')
    async def test():
        oled_clear()
        round = 0
        strikes = 0
        colour_sequence = ['blue','yellow', 'green', 'green', 'green',  'green',  'green',  'green',  'green',  'green',  'red']
        first_time = False
        simon_test = SimonSays(3,8,9,10,11,12,13,14,15)

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
                    
                    elif results == 'LOSE':
                        print(results)
                        return results
                    
                    round, strikes, colour_sequence = results
                    break
                await asyncio.sleep(0.1)

    asyncio.run(test())
    buzzer_stop(8)
