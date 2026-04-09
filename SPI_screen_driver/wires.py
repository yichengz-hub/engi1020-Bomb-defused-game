import random
import time
import sys
from OLEDDriver import OLEDDriver

# --- CONFIG ---
PORT = '/dev/tty.usbserial-0001'
BTN_NEXT = 3   
BTN_CUT = 2   

# --- FIRMWARE COLOR MAPPING ---
WHITE, RED, GREEN, BLUE, YELLOW, GREY, BLACK = 0, 1, 2, 3, 4, 5, 10

class WiresGame:
    def __init__(self, lcd):
        self.lcd = lcd
        # Force a short timeout so the script CANNOT hang forever
        self.lcd.ser.timeout = 0.05 
        print("Game Initialized. Drawing board...")
        self.reset()

    def get_correct_wire(self, wires):
        count = len(wires)
        r, b, y, w, bk = [wires.count(RED), wires.count(BLUE), wires.count(YELLOW), 
                          wires.count(WHITE), wires.count(BLACK)]
        
        if count == 3:
            if r == 0: return 1
            if wires[-1] == WHITE: return 2
            if b > 1: return len(wires) - 1 - wires[::-1].index(BLUE)
            return 2
        elif count == 4:
            if y == 1 and r == 0: return 0
            if b == 1: return 0
            if y > 1: return 3
            return 1
        elif count == 5:
            if r == 1 and y > 1: return 0
            if bk == 0: return 1
            return 0
        elif count == 6:
            if y == 1 and w > 1: return 3
            if r == 0: return 5
            return 3
        return 0

    def reset(self):
        self.lcd.ser.reset_input_buffer()
        self.wire_count = random.randint(3, 6)
        self.wires = [random.choice([RED, BLUE, YELLOW, WHITE, BLACK]) for _ in range(self.wire_count)]
        self.selected = 0
        self.correct = self.get_correct_wire(self.wires)
        
        # Draw Board
        self.lcd._send_rect(0, 0, 240, 320, GREY)
        time.sleep(0.1)
        self.lcd._send_text(45, 15, "DEFUSE BOMB", 2, BLACK)
        
        for i in range(self.wire_count):
            y = 70 + (i * 40)
            self.lcd._send_rect(60, y, 140, 18, self.wires[i])
            time.sleep(0.04)
        
        self.draw_selector(self.selected, WHITE)
        print(f"Target Wire Index: {self.correct}")

    def draw_selector(self, index, color):
        y = 75 + (index * 40)
        self.lcd._send_rect(15, y, 30, 10, color)

    def run(self):
        last_n, last_c = 0, 0
        print("Starting Loop. Polling buttons...")
        
        # Ensure we start with a clean state
        self.lcd.ser.reset_input_buffer()

        while True:
            try:
                # 1. Read NEXT button (Pin 3)
                # We use the driver's digital_read which handles the serial timing
                n_val = self.lcd.digital_read(BTN_NEXT)

                # 2. Read CUT button (Pin 2)
                c_val = self.lcd.digital_read(BTN_CUT)

                # 3. Logic: Cycle through wires on "Press" (Transition from 0 to 1)
                if n_val == 1 and last_n == 0:
                    print("Next Button Pressed")
                    self.draw_selector(self.selected, GREY) # Erase old
                    self.selected = (self.selected + 1) % self.wire_count
                    self.draw_selector(self.selected, WHITE) # Draw new

                # 4. Logic: Cut selected wire on "Press"
                if c_val == 1 and last_c == 0:
                    print(f"Wire Cut! Selected: {self.selected}, Correct: {self.correct}")
                    if self.selected == self.correct:
                        self.lcd._send_rect(0, 0, 240, 320, GREEN)
                        self.lcd._send_text(40, 120, "SAFE!", 3, WHITE)
                        time.sleep(1.5)
                        return "win" 
                    else:
                        self.lcd._send_rect(0, 0, 240, 320, RED)
                        self.lcd._send_text(40, 120, "BOOM!", 4, WHITE)
                        time.sleep(1.5)
                        return "lose"

                # 5. Update "last" states for the next loop iteration
                last_n, last_c = n_val, c_val
                
                # Small delay to prevent CPU slamming and bouncing
                time.sleep(0.05)
                
            except Exception as e:
                print(f"Error in loop: {e}")
                # Only reset buffer if an actual error occurs
                self.lcd.ser.reset_input_buffer()
                time.sleep(0.1)

if __name__ == "__main__":
    try:
        driver = OLEDDriver(port=PORT)
        game = WiresGame(driver)
        
        # 1. Run the game
        final_result = game.run()
        
        # 2. Print result (This MUST execute now)
        print("\n" + "*"*30)
        print(f" FINAL STATUS: {final_result.upper()} ")
        print("*"*30 + "\n")
        
    except KeyboardInterrupt:
        print("\nUser quit the game.")
    finally:
        print("Program closed.")
        sys.exit()