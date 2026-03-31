from engi1020.arduino.api import *
import asyncio
from random import choice
from time import time

class SimonSays():
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
        self.r_frequency = 500
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

        self.matching_colours = [colour for colour in self.mapping[self.strikes].values()]
        self.input_colour_sequence = [self.mapping[self.strikes][color] for color in self.colour_sequence]

        print(self.matching_colours)

        


    async def increase_round(self):
        index = choice(range(len(self.colours)))
        self.colour_sequence.append(self.colours[index])
        self.input_colour_sequence.append(self.matching_colours[index])
        self.current_round += 1
        await asyncio.sleep(0.05)


    async def play(self):
        while True:
            # If all rounds are complete, the user wins the game, and the loop ends.
            if self.current_round > self.total_rounds:
                print("You win the game!")
                return 'WIN'
            
            elif self.strikes >= self.max_strikes:
                print("You lose the game!")
                digital_write(self.r_led, True)
                buzzer_note(self.buzzer_pin, self.strike_frequency, self.game_loose_time)
                await asyncio.sleep(self.game_loose_time)
                digital_write(self.r_led, False)
                return 'LOSE'

            # Check if the round needs to be increased, if it does, add a random colour to the sequence.
            if self.next_round == True:
                index = choice(range(len(self.colours)))
                self.colour_sequence.append(self.colours[index])
                self.input_colour_sequence.append(self.matching_colours[index])
                self.current_round += 1
                self.next_round = False
            
            for colour in self.colour_sequence:
                if colour == 'red':
                    print("red")
                    digital_write(self.r_led, True)
                    buzzer_note(self.buzzer_pin, self.r_frequency, self.colour_time)
                    await asyncio.sleep(self.colour_time)
                    digital_write(self.r_led, False)
                elif colour == 'blue':
                    print("blue")
                    digital_write(self.b_led, True)
                    buzzer_note(self.buzzer_pin, self.b_frequency, self.colour_time)
                    await asyncio.sleep(self.colour_time)
                    digital_write(self.b_led, False)
                elif colour == 'yellow':
                    print("yellow")
                    digital_write(self.r_led, True)
                    digital_write(self.g_led, True)
                    buzzer_note(self.buzzer_pin, self.y_frequency, self.colour_time)
                    await asyncio.sleep(self.colour_time)
                    digital_write(self.g_led, False)
                    digital_write(self.r_led, False)
                else:
                    print("green")
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
                print("Checking input...")
                if r_input == True:
                    first_input = 'red'
                    print("red inputted")
                    digital_write(self.r_led, True)
                    buzzer_note(self.buzzer_pin, self.r_frequency, self.colour_time)
                    await asyncio.sleep(self.colour_time)
                    digital_write(self.r_led, False)
                    break
                elif b_input == True:
                    first_input = 'blue'
                    print("blue inputted")
                    digital_write(self.b_led, True)
                    buzzer_note(self.buzzer_pin, self.b_frequency, self.colour_time)
                    await asyncio.sleep(self.colour_time)
                    digital_write(self.b_led, False) 
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
                    break
                elif g_input == True:   
                    first_input = 'green'
                    print("green inputted")
                    digital_write(self.g_led, True)
                    buzzer_note(self.buzzer_pin, self.g_frequency,  self.colour_time)
                    await asyncio.sleep(self.colour_time)
                    digital_write(self.g_led, False)
                    break
                
                # If nothing is inputted for 2 seconds, the colours begin to play again.
                if time() - start_time > 2:
                    print("Time's up! The colours will play again.")
                    first_input = 'timeout'
                    break

                await asyncio.sleep(0.05)
            

            # The user has entered an input, start the sequence of checking the next inputs
            if first_input != 'timeout':

                start_time = time()
                inputted_sequence = [first_input]
                input_count = 0

                print("\nwaiting for future inputs...")
                while True:
                    # If an element of the inputted sequence is not the same as the colour sequence for the same index,
                    # Then the user gets a strike and the colours play again.
                    if not inputted_sequence[input_count] == self.input_colour_sequence[input_count]:
                        self.strikes += 1
                        print(f"You got a strike, total number is: {self.strikes}")
                        digital_write(self.r_led, True)
                        buzzer_note(self.buzzer_pin, self.strike_frequency, self.strike_time)
                        await asyncio.sleep(self.strike_time)
                        digital_write(self.r_led, False)
                        await asyncio.sleep(0.1)
                        buzzer_note(self.buzzer_pin, self.strike_frequency, self.strike_time)
                        digital_write(self.r_led, True)
                        await asyncio.sleep(self.strike_time)
                        digital_write(self.r_led, False)
                        await asyncio.sleep(self.colour_time + 0.5)
                        return self.current_round, self.strikes, self.colour_sequence
                    
                    # If the inputted sequence is exactly the same as the colour sequence,
                    # then the user wins the round and we increase the round number by 1.  
                    elif inputted_sequence == self.input_colour_sequence:
                        self.next_round = True
                        print("Round complete!")
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
                    elif b_input == True:
                        inputted_sequence.append('blue')
                        print("blue inputted")
                        input_count += 1
                        start_time = time()
                        digital_write(self.b_led, True)
                        buzzer_note(self.buzzer_pin, self.b_frequency, self.colour_time)
                        await asyncio.sleep(self.colour_time)
                        digital_write(self.b_led, False)
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
                    elif g_input == True:
                        inputted_sequence.append('green')
                        print("green inputted")
                        input_count += 1
                        start_time = time()
                        digital_write(self.g_led, True)
                        buzzer_note(self.buzzer_pin, self.g_frequency, self.colour_time)
                        await asyncio.sleep(self.colour_time)
                        digital_write(self.g_led, False)

                    if time() - start_time > 2:
                        # you get a strike if the above condition is true
                        self.strikes += 1
                        print(f"You got a strike, total number is: {self.strikes}")
                        digital_write(self.r_led, True)
                        buzzer_note(self.buzzer_pin, self.strike_frequency, self.strike_time)
                        await asyncio.sleep(self.strike_time)
                        digital_write(self.r_led, False)
                        await asyncio.sleep(0.1)
                        buzzer_note(self.buzzer_pin, self.strike_frequency, self.strike_time)
                        digital_write(self.r_led, True)
                        await asyncio.sleep(self.strike_time)
                        digital_write(self.r_led, False)
                        await asyncio.sleep(self.colour_time + 0.5)
                        return self.current_round, self.strikes, self.colour_sequence
                    
                    await asyncio.sleep(0.1)
