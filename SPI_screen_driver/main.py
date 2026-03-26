import time
from LCDDriver import LCDDriver

# Initialize with Portrait dimensions
# Port might need to be changed to your specific one
lcd = LCDDriver('/dev/tty.usbserial-0001', baudrate=115200, width=240, height=320)

def draw_wire_game():
    lcd.clear()
    lcd.draw_text(10, 10, "BOMB UNIT", size=3, color=1) # Red Title
    lcd.draw_text(10, 45, "PORTRAIT MODE", size=1, color=0)
    
    # Wire Y positions: 70, 110, 150, 190, 230, 270
    # Colors: 1=Red, 2=Green, 3=Blue, 4=Yellow, 0=White
    wire_setup = [
        {'y': 70,  'col': 1}, 
        {'y': 110, 'col': 2}, 
        {'y': 150, 'col': 3}, 
        {'y': 190, 'col': 4}, 
        {'y': 230, 'col': 0}, 
        {'y': 270, 'col': 1}
    ]
    
    for i, w in enumerate(wire_setup):
        # Draw a thick wire across the 240px width
        lcd.draw_wire(20, w['y'], w=200, h=20, color=w['col'])
        # Draw the label
        lcd.draw_text(100, w['y'] + 2, str(i+1), size=2, color=10) # Black text on the wire
        
    lcd.update()
    return wire_setup

wires = draw_wire_game()

while True:
    choice = input("\nSelect wire to cut (1-6), 'r' to reset, or 's' to stop: ")
    
    if choice.lower() == 's':
        print("Game Stopped!")
        lcd.clear()
        break

    if choice.lower() == 'r':
        wires = draw_wire_game()
        continue

    if choice.isdigit():
        num = int(choice)
        if 1 <= num <= 6:
            y_pos = wires[num-1]['y']
            print(f"Cutting wire {num}...")
            
            # Draw a black vertical "snip" mark in the middle of the wire
            # x=110 (middle-ish), y=wire_y, width=20, height=20, color=10 (Black)
            lcd._send_rect(110, y_pos, 20, 20, color=10)
            print("Cut successful!")
        else:
            print("Wire does not exist!")