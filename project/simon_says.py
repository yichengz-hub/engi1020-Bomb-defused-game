from engi1020.arduino.api import *
import asyncio
from random import choice
from time import time

class SimonSays():
    def __init__(self, round_number,  buzzer_pin, r_button, y_button, b_button, g_button, r_led, g_led, b_led ):
        self.round_number = round_number
        self.buzzer_pin = buzzer_pin
        self.r_button = r_button
        self.y_button = y_button
        self.b_button = b_button
        self.g_button = g_button
        self.r_led = r_led
        self.g_led = g_led
        self.b_led = b_led


    def start(self):
        self.r_frequency = 247*2
        self.y_frequency = 311*2
        self.b_frequency = 415*2
        self.g_frequency = 500*2
        self.colour_time = 0.8
        self.next_round = False
        self.current_round = 0
        self.strikes = 0
        self.colour_sequence = ['red', 'blue', 'yellow', 'green']
        self.colours = ['red', 'blue', 'yellow', 'green']


    async def increase_round(self):
        self.colour_sequence.append(choice(self.colours))
        await asyncio.sleep(0.1)


    async def play(self):
        # If all rounds are complete, the user wins the game, and the loop ends.
        if self.current_round >= self.round_number:
            print("You win the game!")
            return
        
        elif self.strikes >= 3:
            print("You lose the game!")
            return

        # Check if the round needs to be increased, if it does, add a random colour to the sequence.
        if self.next_round == True:
            self.colour_sequence.append(choice(self.colours))
            self.next_round = False
        
        for colour in self.colour_sequence:
            if colour == 'red':
                print("red")
                digital_write(self.r_led, True)
                buzzer_frequency(self.buzzer_pin, self.r_frequency)
                await asyncio.sleep(self.colour_time)
                digital_write(self.r_led, False)
                buzzer_stop(self.buzzer_pin)
            elif colour == 'blue':
                print("blue")
                digital_write(self.b_led, True)
                buzzer_frequency(self.buzzer_pin, self.b_frequency)
                await asyncio.sleep(self.colour_time)
                digital_write(self.b_led, False)
                buzzer_stop(self.buzzer_pin)
            elif colour == 'yellow':
                print("yellow")
                digital_write(self.r_led, True)
                digital_write(self.g_led, True)
                buzzer_frequency(self.buzzer_pin, self.y_frequency)
                await asyncio.sleep(self.colour_time)
                digital_write(self.r_led, False)
                digital_write(self.g_led, False)
                buzzer_stop(self.buzzer_pin)
            else:
                print("green")
                digital_write(self.g_led, True)
                buzzer_frequency(self.buzzer_pin, self.g_frequency)
                await asyncio.sleep(self.colour_time)
                digital_write(self.g_led, False)
                buzzer_stop(self.buzzer_pin)


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
                break
            elif b_input == True:
                first_input = 'blue'
                print("blue inputted")  
                break
            elif y_input == True:
                first_input = 'yellow'
                print("yellow inputted")
                break
            elif g_input == True:   
                first_input = 'green'
                print("green inputted")
                break
            
            # If nothing is inputted for 2 seconds, the colours begin to play again.
            if time() - start_time > 2:
                print("Time's up! The colours will play again.")
                first_input = 'timeout'
                break

            await asyncio.sleep(1)
        

        # The user has entered an input, start the sequence of checking the next inputs
        if first_input != 'timeout':

            start_time = time()
            inputted_sequence = [first_input]
            input_count = 0

            print("waiting for future inputs...")
            while True:
                # If an element of the inputted sequence is not the same as the colour sequence for the same index,
                # Then the user gets a strike and the colours play again.
                if not inputted_sequence[input_count] == self.colour_sequence[input_count]:
                    self.strikes += 1
                    print(f"You got a strike, total number is: {self.strikes}")
                    break
                
                # If the inputted sequence is exactly the same as the colour sequence,
                # then the user wins the round and we increase the round number by 1.  
                elif inputted_sequence == self.colour_sequence:
                    self.current_round += 1
                    self.next_round = True
                    print("Round complete!")
                    break

                r_input = digital_read(self.r_button)
                b_input = digital_read(self.b_button)
                y_input = digital_read(self.y_button)
                g_input = digital_read(self.g_button)

                if r_input == True:
                    inputted_sequence.append('red')
                    input_count += 1
                    start_time = time()  
                    digital_write(self.r_led, True)
                    buzzer_frequency(self.buzzer_pin, self.r_frequency)
                    await asyncio.sleep(self.colour_time)
                    digital_write(self.r_led, False)
                    buzzer_stop(self.buzzer_pin)
                elif b_input == True:
                    inputted_sequence.append('blue')
                    input_count += 1
                    start_time = time()
                    digital_write(self.b_led, True)
                    buzzer_frequency(self.buzzer_pin, self.b_frequency)
                    await asyncio.sleep(self.colour_time)
                    digital_write(self.b_led, False)
                    buzzer_stop(self.buzzer_pin)
                elif y_input == True:
                    inputted_sequence.append('yellow')
                    input_count += 1
                    start_time = time()
                    digital_write(self.r_led, True)
                    digital_write(self.g_led, True)
                    buzzer_frequency(self.buzzer_pin, self.y_frequency)
                    await asyncio.sleep(self.colour_time)
                    digital_write(self.r_led, False)
                    digital_write(self.g_led, False)
                    buzzer_stop(self.buzzer_pin)
                elif g_input == True:
                    inputted_sequence.append('green')
                    input_count += 1
                    start_time = time()
                    digital_write(self.g_led, True)
                    buzzer_frequency(self.buzzer_pin, self.g_frequency)
                    await asyncio.sleep(self.colour_time)
                    digital_write(self.g_led, False)
                    buzzer_stop(self.buzzer_pin)

                if time() - start_time > 2:
                    # you get a strike if the above condition is true
                    self.strikes += 1
                    print(f"You got a strike, total number is: {self.strikes}")
                    break
                
                await asyncio.sleep(0.1)
