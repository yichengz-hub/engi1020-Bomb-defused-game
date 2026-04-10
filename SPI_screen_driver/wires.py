import time
import random
import sys
from OLEDDriver import OLEDDriver

# Color Constants
WHITE, RED, GREEN, BLUE, YELLOW, GREY, BLACK = 0, 1, 2, 3, 4, 5, 10

class WiresGame:
    def __init__(self, oled):
        self.oled = oled

        # Buttons (Matching your Maze logic pins)
        self.PIN_NEXT = 3   # Move selection
        self.PIN_CUT = 2    # Confirm selection

        self.reset()

    def get_correct_wire(self, wires):
        """Standard bomb-defusal logic for wire cutting - Hard Mode."""
        count = len(wires)
        # Color counts
        r, b, y, w, bk = [wires.count(RED), wires.count(BLUE), wires.count(YELLOW), 
                          wires.count(WHITE), wires.count(BLACK)]
        
        # 3 WIRES
        if count == 3:
            # If no red wires, cut second
            if r == 0: return 1
            # Else if exactly one white and first wire is red, cut first
            elif w == 1 and wires[0] == RED: return 0
            # Else if more than one blue, cut the last blue wire
            elif b > 1: return len(wires) - 1 - wires[::-1].index(BLUE)
            # Otherwise, cut the last wire
            return 2

        # 4 WIRES
        elif count == 4:
            # If more than one red and last wire is yellow, cut last red
            if r > 1 and wires[-1] == YELLOW: return len(wires) - 1 - wires[::-1].index(RED)
            # Else if exactly one yellow and no red wires, cut the first wire
            elif y == 1 and r == 0: return 0
            # Else if exactly one blue wire, cut the first wire
            elif b == 1: return 0
            # Else if more than one yellow, cut the last wire
            elif y > 1: return 3
            # Otherwise, cut the second wire
            return 1

        # 5 WIRES
        elif count == 5:
            # If last wire is black and there is at least one red, cut the fourth wire
            if wires[-1] == BLACK and r > 0: return 3
            # Else if exactly one red and more than one yellow, cut the first wire
            elif r == 1 and y > 1: return 0
            # Else if no black wires, cut the second wire
            elif bk == 0: return 1
            # Otherwise, cut the first wire
            return 0

        # 6 WIRES
        elif count == 6:
            # If no yellow wires and the first wire is white, cut the third wire
            if y == 0 and wires[0] == WHITE: return 2
            # Else if exactly one yellow and more than one white, cut the fourth wire
            elif y == 1 and w > 1: return 3
            # Else if no red wires, cut the last wire
            elif r == 0: return 5
            # Otherwise, cut the fourth wire
            return 3

        return 0

    def draw_selector(self, index, color):
        """Draws the selection arrow/indicator."""
        y = 75 + (index * 40)
        # Draws a small rectangle next to the wire
        self.oled._send_rect(15, y, 30, 10, color)

    def reset(self):
        """Clears screen and generates new wires."""
        self.oled.ser.write(b'C') # Clear screen command
        time.sleep(0.1)
        
        self.wire_count = random.randint(3, 6)
        self.wires = [random.choice([RED, BLUE, YELLOW, WHITE, BLACK]) for _ in range(self.wire_count)]
        self.selected = 0
        self.correct = self.get_correct_wire(self.wires)

        # Draw Background and Header
        self.oled._send_rect(0, 0, 240, 320, GREY)
        self.oled._send_text(45, 15, "WIRES", 2, BLACK)
        
        # Draw Wires
        for i in range(self.wire_count):
            y = 70 + (i * 40)
            self.oled._send_rect(60, y, 140, 18, self.wires[i])
            time.sleep(0.04)
        
        self.draw_selector(self.selected, WHITE)
        print(f"Target Wire Index: {self.correct}")

    def run(self):
        """Main game loop using the same structure as MazeGame."""
        print("Wires Active. Choose carefully...")
        last_states = {p: 0 for p in [self.PIN_NEXT, self.PIN_CUT]}
        
        while True:
            try:
                # 1. Check NEXT button (Move selector)
                val_next = self.oled.digital_read(self.PIN_NEXT)
                if val_next == 1 and last_states[self.PIN_NEXT] == 0:
                    self.draw_selector(self.selected, GREY) # Erase old
                    self.selected = (self.selected + 1) % self.wire_count
                    self.draw_selector(self.selected, WHITE) # Draw new
                last_states[self.PIN_NEXT] = val_next

                # 2. Check CUT button (Verify win/loss)
                val_cut = self.oled.digital_read(self.PIN_CUT)
                if val_cut == 1 and last_states[self.PIN_CUT] == 0:
                    self.oled.ser.write(b'C') # Clear screen
                    time.sleep(0.1)

                    if self.selected == self.correct:
                        self.oled._send_rect(0, 0, 240, 320, GREEN)
                        self.oled._send_text(40, 120, "SAFE!", 3, WHITE)
                        time.sleep(1.5)
                        self.oled.ser.reset_input_buffer()
                        return "win" 
                    else:
                        self.oled._send_rect(0, 0, 240, 320, RED)
                        self.oled._send_text(40, 120, "BOOM!", 4, WHITE)
                        time.sleep(1.5)
                        self.oled.ser.reset_input_buffer()
                        return "loss" # Matching MazeGame "loss" string
                last_states[self.PIN_CUT] = val_cut

                time.sleep(0.02) # Fast polling like Maze

            except Exception:
                self.oled.ser.reset_input_buffer()

if __name__ == "__main__":
    driver = OLEDDriver(port='/dev/tty.usbserial-0001')
    game = WiresGame(driver)
    final_result = game.run()
    print(f"Final Wires State: {final_result}")
    