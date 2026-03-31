from engi1020.arduino.api import *
from time import sleep

# This is the "official" way the lab wants you to print.
# If your Freenove LCD is lucky, it might respond to this.
rgb_lcd_print("Hello World hello hello hello")

rgb_lcd_print("Bottom Line", row=1, col=0)

buzzer_note(13,500,2)
print('hi')