from engi1020.arduino.api import *
from random import choice, choices, shuffle
import time
import asyncio

class Passwords:
    def __init__(self, cycle_btn, column_btn, submit_btn):
        self.cycle_btn = cycle_btn
        self.column_btn = column_btn
        self.submit_btn = submit_btn
        self.current_column = 0
        
        self.all_words = [

            "about", "after", "again", "below", "could",
            "every", "first", "found", "great", "house",
            "large", "learn", "never", "other", "place",
            "plant", "point", "right", "small", "sound",
            "spell", "still", "study", "their", "there",
            "these", "thing", "think", "three", "water",
            "where", "which", "world", "would", "write"
        ]

        self.game_init()


    def game_init(self):
        self.word = choice(self.all_words)
        
        self.columns = []
        all_chars = "abcdefghijklmnopqrstuvwxyz"
        
        for i in range(5):
            col = [self.word[i]] + choices(all_chars, k=5)
            shuffle(col)
            self.columns.append(col)


    def cycle_letter(self):
        col = self.columns[self.current_column]
        self.columns[self.current_column] = col[1:] + [col[0]]


    def lcd_display(self):
        rgb_lcd_clear() 
        
        display_word = "".join([col[0] for col in self.columns])

        rgb_lcd_print(display_word, row=0, col=0)

        cursor = " " * self.current_column + "^"
        rgb_lcd_print(cursor, row=1, col=0)
    

    def check_guess(self):
        result = "".join([c[0] for c in self.columns])
        if result == self.word:
            rgb_lcd_print("DISARMED", "GOOD JOB")
            return True
        else:
            time.sleep(0.3)
            return False
        

    def finish_cond(self):
        self.result = "".join([col[0] for col in self.columns])

        if self.result == self.word:
            print("CORRECT! Bomb Disarmed.")
            rgb_lcd_clear()
            return "WIN"

        else:
            print(f"WRONG: {self.result.upper()} is not the password.")
            rgb_lcd_clear()
            return "LOSE"


    async def game_loop(self):
        self.lcd_display()
        print(self.word)
        
        while True:
            if digital_read(self.cycle_btn):
                self.cycle_letter()
                self.lcd_display()
                while digital_read(self.cycle_btn): time.sleep(0.01)

            if digital_read(self.column_btn):
                self.current_column = (self.current_column + 1) % 5
                self.lcd_display()
                while digital_read(self.column_btn): time.sleep(0.01)

            if digital_read(self.submit_btn):
                result = self.finish_cond()

                while digital_read(self.submit_btn):
                    time.sleep(0.01)
 
                return result
            
            time.sleep(0.05)
            await asyncio.sleep(0.02)


if __name__ == '__main__':
    digital_write(4, False)
    digital_write(7, False)
    game = Passwords(8,9,10)
    time.sleep(2)
    game.game_loop()
