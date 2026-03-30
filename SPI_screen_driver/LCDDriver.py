import serial
import time

class LCDDriver:
    """Python driver for Arduino Waveshare LCD with hardware IO support"""

    def __init__(self, port='/dev/tty.usbserial-0001', baudrate=115200, width=240, height=320):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Give the Arduino time to reboot
        self.ser.reset_input_buffer()
        self.objects = []  
        self.init_screen(width, height)

    def _wait_for_ack(self):
        """Block Python script until the Arduino replies with 'K'"""
        while True:
            if self.ser.in_waiting > 0:
                response = self.ser.read()
                if response == b'K':
                    break

    def init_screen(self, w, h):
        self.ser.write(b'I')
        self.ser.write(w.to_bytes(2, 'little'))
        self.ser.write(h.to_bytes(2, 'little'))
        self._wait_for_ack()

    # --- Hardware IO Methods ---
    def digital_read(self, pin):
        """Sends a read command and returns 0 or 1."""
        # 1. Clear any leftover junk in the buffer before asking for a new read
        self.ser.reset_input_buffer()
        
        # 2. Send Command
        self.ser.write(b'D') 
        self.ser.write(bytes([pin]))
        
        # 3. Wait for data with a timeout
        start_time = time.time()
        while self.ser.in_waiting == 0:
            if time.time() - start_time > 1.0:
                print(f"Error: Timeout reading pin {pin}")
                return 0
        
        # 4. Read and Decode
        raw_data = self.ser.read(1)
        
        # Logic: Convert bytes to string, then check if it's '1'
        # This works whether your Arduino uses Serial.print() or Serial.write()
        if raw_data == b'1' or raw_data == b'\x01':
            return 1
        else:
            return 0
        
    def digital_write(self, pin, state):
        """Sets a pin to state (0=LOW, 1=HIGH). Sets pin to OUTPUT."""
        self.ser.write(b'L')
        self.ser.write(bytes([pin, 1 if state else 0]))
        self._wait_for_ack()

    # --- Screen Management ---
    def clear(self):
        self.ser.write(b'C')
        self._wait_for_ack()
        self.objects = []

    # --- Object storage (for batch updates) ---
    def draw_rect(self, x, y, w, h, color=0):
        self.objects.append(('rect', x, y, w, h, color))

    def draw_circle(self, x, y, r, color=0):
        self.objects.append(('circle', x, y, r, color))

    def draw_triangle(self, x0, y0, x1, y1, x2, y2, color=0):
        self.objects.append(('triangle', x0, y0, x1, y1, x2, y2, color))

    def draw_wire(self, x, y, w=200, h=10, color=0):
        self.objects.append(('wire', x, y, w, h, color))

    def cut_wire(self, x, y, w=200, h=10):
        self.objects.append(('rect', x, y, w, h, 10)) # Using 10 (Black) as the eraser

    def draw_text(self, x, y, text, size=1, color=0):
        self.objects.append(('text', x, y, text, size, color))

    def update(self):
        """Redraw all stored objects to the screen"""
        self.ser.write(b'C')
        self._wait_for_ack()

        for obj in self.objects:
            if obj[0] == 'rect': self._send_rect(*obj[1:])
            elif obj[0] == 'circle': self._send_circle(*obj[1:])
            elif obj[0] == 'triangle': self._send_triangle(*obj[1:])
            elif obj[0] == 'wire': self._send_wire(*obj[1:])
            elif obj[0] == 'text': self._send_text(*obj[1:])

    # --- Private Serial Protocols ---
    def _send_rect(self, x, y, w, h, color):
        self.ser.write(b'R')
        self.ser.write(x.to_bytes(2,'little'))
        self.ser.write(y.to_bytes(2,'little'))
        self.ser.write(w.to_bytes(2,'little'))
        self.ser.write(h.to_bytes(2,'little'))
        self.ser.write(bytes([color]))
        self._wait_for_ack()

    def _send_circle(self, x, y, r, color):
        self.ser.write(b'O')
        self.ser.write(x.to_bytes(2,'little'))
        self.ser.write(y.to_bytes(2,'little'))
        self.ser.write(r.to_bytes(2,'little'))
        self.ser.write(bytes([color]))
        self._wait_for_ack()

    def _send_triangle(self, x0, y0, x1, y1, x2, y2, color):
        self.ser.write(b'G')
        self.ser.write(x0.to_bytes(2,'little'))
        self.ser.write(y0.to_bytes(2,'little'))
        self.ser.write(x1.to_bytes(2,'little'))
        self.ser.write(y1.to_bytes(2,'little'))
        self.ser.write(x2.to_bytes(2,'little'))
        self.ser.write(y2.to_bytes(2,'little'))
        self.ser.write(bytes([color]))
        self._wait_for_ack()

    def _send_wire(self, x, y, w, h, color):
        self.ser.write(b'W')
        self.ser.write(x.to_bytes(2,'little'))
        self.ser.write(y.to_bytes(2,'little'))
        self.ser.write(w.to_bytes(2,'little'))
        self.ser.write(h.to_bytes(2,'little'))
        self.ser.write(bytes([color]))
        self._wait_for_ack()

    def _send_text(self, x, y, text, size, color):
        self.ser.write(b'T')
        self.ser.write(x.to_bytes(2,'little'))
        self.ser.write(y.to_bytes(2,'little'))
        self.ser.write(bytes([size, color, len(text)]))
        self.ser.write(text.encode())
        self._wait_for_ack()