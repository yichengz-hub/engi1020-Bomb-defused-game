import asyncio
from engi1020.arduino.api import *
import morse
from wordfreq import top_n_list
from random import choice

class Morsecode:
    def __init__(self, btn_pin1, btn_pin2, buzzer_pin):
        self.btn_pin1 = btn_pin1
        self.btn_pin2 = btn_pin2
        self.buzzer_pin = buzzer_pin
        self.round_over = False

    def start(self):
        words = top_n_list("en", 50000)
        five_letter_words = [
                                "crane",
                                "blush",
                                "tiger",
                                "flint",
                                "grape",
                                "swept",
                                "pride",
                                "charm",
                                "doubt",
                                "knack",
                                "shard",
                                "vigor",
                                "plume",
                                "truce",
                                "whale"
                            ]

        self.word = choice(five_letter_words)
        self.decode_str = morse.string_to_morse(self.word)
        mapping = {'.': '0', '-': '1'}

        self.seq = ["".join(mapping[c] for c in code) for code in self.decode_str]
        self.answer = [int(bit) for code in self.seq for bit in code]


        self.input_seq = []
        self.round_over = False
        print(f"DEBUG: Word is '{self.word}', Morse sequence: {self.answer}")

    async def play(self):
        while not self.round_over:
            for beats in self.seq:
                for beat in beats:
                    if self.round_over:
                        buzzer_stop(self.buzzer_pin)
                        return
                    
                    if beat == '1':
                        buzzer_note(self.buzzer_pin, 2500, 0.5)

                    else:
                        buzzer_note(self.buzzer_pin, 2500, 0.1)
                    await asyncio.sleep(0.5)
                await asyncio.sleep(1)

    async def player_input(self):
        while len(self.input_seq) < len(self.answer):
            if digital_read(self.btn_pin1):
                self.input_seq.append(0)
                print("Button 1 pressed")
                await asyncio.sleep(0.13)

            elif digital_read(self.btn_pin2):
                self.input_seq.append(1)
                print("Button 2 pressed")
                await asyncio.sleep(0.13)

            else:
                await asyncio.sleep(0.1)

    async def win_cond(self):
        while len(self.input_seq) < len(self.answer):
            await asyncio.sleep(0.1)
        self.round_over = True
        buzzer_stop(self.buzzer_pin)
        if self.input_seq == self.answer:
            buzzer_note(self.buzzer_pin, 3000, 1.5)
            print("Correct!")
            return 1
        
        else:
            buzzer_note(self.buzzer_pin, 1000, 1.5)
            print("Incorrect!")
            return 0

    async def main(self):
        while True:
            self.start()
            play_task = asyncio.create_task(self.play())
            input_task = asyncio.create_task(self.player_input())
            result = await self.win_cond()
            play_task.cancel()
            input_task.cancel()

            if result == 1:
                print("We WIN")
                return "morse win"
            
            else:
                print("We LOSE")
                return "morse lose"