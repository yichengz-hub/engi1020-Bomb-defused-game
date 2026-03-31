import asyncio
from engi1020.arduino.api import *
import morse
from random import choice
from time import time

class MorseCode:
    def __init__(self, dot_pin, dash_pin, buzzer_pin):
        self.dot_pin = dot_pin
        self.dash_pin = dash_pin
        self.buzzer_pin = buzzer_pin


    def start(self, current_strikes):
        five_letter_words = {
                                "shell": "shark",
                                "halls": "porch",
                                "slick": "glide",
                                "trick": "prank",
                                "boxes": "cargo",
                                "leaks": "dripy",
                                "strobe": "flashy",
                                "bistro": "dinner",
                                "flick": "light",
                                "bombs": "blast",
                                "break": "crush",
                                "brick": "stone",
                                "steak": "roast",
                                "sting": "wasps",
                                "vector": "scalar",
                                "beats": "drums",
                            }
        
        self.current_strikes = current_strikes
        self.output_word = choice(list(five_letter_words.keys()))
        self.input_word = five_letter_words[self.output_word]
        mapping = {'.': '0', '-': '1'}
        print(f'output word: {self.output_word}')
        print(f'input word: {self.input_word}')
        
        self.decode_str_output = morse.string_to_morse(self.output_word)

        self.decode_str_input = morse.string_to_morse(self.input_word)

        self.output_seq = ["".join(mapping[c] for c in code) for code in self.decode_str_output]
        print(f'self.seq: {self.output_seq}')

        self.input_seq = ["".join(mapping[c] for c in code) for code in self.decode_str_input]
        print(f'self.seq: {self.input_seq}')
        
        self.answer = [int(bit) for code in self.input_seq for bit in code]
        print(f'self.answer: {self.answer}')

        self.input_seq = []
        self.win_game = False


    async def play(self):
        while True:
            for beats in self.output_seq:
                for beat in beats:
                    if self.win_game:
                        buzzer_stop(self.buzzer_pin)
                        return
                    
                    if beat == '1':
                        digital_write(self.buzzer_pin, True)
                        await asyncio.sleep(0.25)
                        digital_write(self.buzzer_pin, False)

                    else:
                        digital_write(self.buzzer_pin, True)
                        await asyncio.sleep(0.1)
                        digital_write(self.buzzer_pin, False)

                    await asyncio.sleep(0.25)
                await asyncio.sleep(0.5)
            await asyncio.sleep(1)


    async def check_for_input(self):
        while True:
            if digital_read(self.dot_pin):
                first_input = 0
                return first_input
            elif digital_read(self.dash_pin):
                first_input = 1
                return first_input
            await asyncio.sleep(0.05)


    async def player_input(self, first_input):
            self.input_seq.append(first_input)
            start_time = time()
            inputted_sequence = [first_input]
            input_count = 0
                
            if first_input == 0:
                print("Dot")
                digital_write(self.buzzer_pin, True)
                await asyncio.sleep(0.1)
                digital_write(self.buzzer_pin, False)
            else:
                print("Dash")
                digital_write(self.buzzer_pin, True)
                await asyncio.sleep(0.25)
                digital_write(self.buzzer_pin, False)

            while True:
                if not inputted_sequence[input_count] == self.answer[input_count]:
                    return 'strike'

                if inputted_sequence == self.answer:
                    return 'win'

                if digital_read(self.dot_pin):
                    self.input_seq.append(0)
                    print("Dot")
                    start_time = time()
                    inputted_sequence.append(0)
                    input_count += 1
                    digital_write(self.buzzer_pin, True)
                    await asyncio.sleep(0.1)
                    digital_write(self.buzzer_pin, False)

                elif digital_read(self.dash_pin):
                    self.input_seq.append(1)
                    print("Dash")
                    start_time = time()
                    inputted_sequence.append(1)
                    input_count += 1
                    digital_write(self.buzzer_pin, True)
                    await asyncio.sleep(0.25)
                    digital_write(self.buzzer_pin, False)

                if time() - start_time > 2:
                    return 'strike'

                await asyncio.sleep(0.1)


    async def main(self):
        while True:
            play_task = asyncio.create_task(self.play())
            check_for_input_task = asyncio.create_task(self.check_for_input())

            while True:
                if check_for_input_task.done():
                    first_input = await check_for_input_task
                    play_task.cancel()
                    result = await self.player_input(first_input)

                    if result == 'win':
                        message = 'WIN'
                        check_for_input_task.cancel()
                        play_task.cancel()
                        print(message)
                        # TODO make the buzzer play a happy sound
                        return message
                    
                    else:
                        print('you get a strike')
                        check_for_input_task.cancel()
                        play_task.cancel()
                        self.current_strikes += 1
                        # TODO make the buzzer play a sad sound
                        return "LOSE"

                await asyncio.sleep(0.1)
