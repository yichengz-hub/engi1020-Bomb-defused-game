from engi1020.arduino.api import *
import asyncio
from random import choice
from time import time

class SimonSays():
    def __init__(self, rounds, buzzer_pin, r_button, y_button, b_button, g_button, r_led, g_led, b_led ):
        self.rounds = rounds
        self.buzzer_pin = buzzer_pin
        self.r_button = r_button
        self.y_button = y_button
        self.b_button = b_button
        self.g_button = g_button
        self.r_led = r_led
        self.g_led = g_led
        self.b_led = b_led


    def start(self):
        self.r_frequency = 252
        self.b_frequency = 415
        self.y_frequency = 310
        self.g_frequency = 209
        self.colour_time = 0.5
        self.colour_sequence = []
        self.colours = ['red', 'blue', 'yellow', 'green']


    async def increase_round(self):
        self.colour_sequence.append(choice(self.colours))


    async def play(self):
        while True:
            for colour in self.colour_sequence:
                if colour == 'red':
                    digital_write(self.r_led, True)
                    buzzer_frequency(self.buzzer_pin, self.r_frequency)
                    await asyncio.sleep(self.colour_time)
                    digital_write(self.r_led, False)
                    buzzer_stop(self.buzzer_pin)
                elif colour == 'blue':
                    digital_write(self.b_led, True)
                    buzzer_frequency(self.buzzer_pin, self.b_frequency)
                    await asyncio.sleep(self.colour_time)
                    digital_write(self.b_led, False)
                    buzzer_stop(self.buzzer_pin)
                elif colour == 'yellow':
                    digital_write(self.r_led, True)
                    digital_write(self.g_led, True)
                    buzzer_frequency(self.buzzer_pin, self.y_frequency)
                    await asyncio.sleep(self.colour_time)
                    digital_write(self.r_led, False)
                    digital_write(self.g_led, False)
                    buzzer_stop(self.buzzer_pin)
                else:
                    digital_write(self.g_led, True)
                    buzzer_frequency(self.buzzer_pin, self.g_frequency)
                    await asyncio.sleep(self.colour_time)
                    digital_write(self.g_led, False)
                    buzzer_stop(self.buzzer_pin)

            start_time = time()
            inputted_sequence = []
            input_count = 0
            while True:
                await asyncio.sleep(0.001)
                r_input = digital_read(self.r_button)
                b_input = digital_read(self.b_button)
                y_input = digital_read(self.y_button)
                g_input = digital_read(self.g_button)

                test_list = self.colour_sequence[:input_count]
                if not test_list == inputted_sequence:
                    # you get a strike if the above condition is true
                    win_round = False
                    strike = True
                    return win_round, strike
                
                elif inputted_sequence == self.colour_sequence:
                    # you win the round, this is the only way to win
                    win_round = True
                    strike = False
                    return win_round, strike

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
                    if input_count == 0:
                        # No strikes, break the loop and start playing the output pattern again
                        break
                    else:
                        strike = True
                        win_round = False
                        return win_round, strike
                    

    async def game_loop_main():
        first_round = play() 
        pass               
    