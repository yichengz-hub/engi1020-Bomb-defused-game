import random
import time
from LCDDriver import LCDDriver

# --- CONFIG ---
PORT = '/dev/tty.usbserial-0001'
BTN_CUT = 2
BTN_NEXT = 3

class WiresGame:
    def __init__(self, lcd):
        self.lcd = lcd
        # Set a very short timeout so we don't hang if an ACK is missed
        self.lcd.ser.timeout = 0.1 
        self.reset()

    def safe_send(self, cmd, *args):
        """Replacement for _wait_for_ack that won't hang the game"""
        self.lcd.ser.write(cmd)
        for val in args:
            if isinstance(val, bytes): self.lcd.ser.write(val)
            elif isinstance(val, int): self.lcd.ser.write(bytes([val]))
        
        # Non-blocking ACK check: Wait max 100ms for 'K'
        start = time.time()
        while time.time() - start < 0.1:
            if self.lcd.ser.in_waiting > 0:
                if self.lcd.ser.read() == b'K':
                    return True
        return False # Move on even if we didn't get an ACK

    def reset(self):
        print("\n--- NEW ROUND ---")
        self.wire_count = random.randint(3, 4)
        self.wires = [random.choice([2, 3, 4, 5]) for _ in range(self.wire_count)]
        self.cut_states = [False] * self.wire_count
        self.selected = 0
        self.correct = random.randint(0, self.wire_count - 1)
        self.state = "playing"
        time.sleep(0.5)
        self.render()

    def render(self):
        print(f"Drawing Frame {self.selected}...", end=" ")
        
        # 1. Clear buffers to stop the deadlock
        self.lcd.ser.reset_input_buffer()
        self.lcd.ser.reset_output_buffer()
        time.sleep(0.05)

        # 2. CLEAR SCREEN (Manual send to avoid the driver's blocking ACK)
        self.safe_send(b'C')

        # 3. DRAW UI (Using direct calls)
        # Text: T, x(2), y(2), size(1), color(1), len(1), string
        self.lcd._send_text(20, 20, "DEFUSE BOMB", 2, 1)

        for i in range(self.wire_count):
            y = 80 + (i * 55)
            color = self.wires[i]
            
            # Wires: R, x(2), y(2), w(2), h(2), color(1)
            if not self.cut_states[i]:
                self.lcd._send_rect(60, y, 140, 18, color)
            else:
                self.lcd._send_rect(60, y, 40, 18, color)
                self.lcd._send_rect(160, y, 40, 18, color)

            # Selector: R (Simple square is faster/safer than Triangle)
            if i == self.selected:
                self.lcd._send_rect(15, y + 4, 25, 10, 1)

        print("Done.")

    def loop(self):
        last_next = 0
        last_cut = 0
        
        while True:
            # 1. Read Inputs
            try:
                nxt = self.lcd.digital_read(BTN_NEXT)
                cut = self.lcd.digital_read(BTN_CUT)
            except:
                continue

            # 2. Cycle Logic
            if nxt == 1 and last_next == 0:
                print("[ACTION] CYCLE")
                self.selected = (self.selected + 1) % self.wire_count
                time.sleep(0.1) # Breathe
                self.render()
                last_next = 1
                continue

            # 3. Cut Logic
            if cut == 1 and last_cut == 0:
                print("[ACTION] CUT")
                if self.state == "playing":
                    self.cut_states[self.selected] = True
                    self.state = "win" if self.selected == self.correct else "strike"
                    print(f" >> {self.state.upper()}")
                
                time.sleep(0.1)
                self.render()
                last_cut = 1
                
                if self.state in ["win", "strike"]:
                    time.sleep(2)
                    self.reset()
                continue

            if nxt == 0: last_next = 0
            if cut == 0: last_cut = 0
            time.sleep(0.04)

if __name__ == "__main__":
    game = WiresGame(LCDDriver(port=PORT))
    game.loop()