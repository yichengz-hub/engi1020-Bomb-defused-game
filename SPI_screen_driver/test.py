# test_buttons.py

import time
from LCDDriver import LCDDriver

BTN_CUT = 2
BTN_NEXT = 3

lcd = LCDDriver('/dev/tty.usbserial-0001')

print("Press buttons...")

while True:
    cut = lcd.digital_read(BTN_CUT)
    nxt = lcd.digital_read(BTN_NEXT)

    print(f"CUT: {cut} | NEXT: {nxt}")

    time.sleep(0.2)