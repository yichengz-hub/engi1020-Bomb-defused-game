import serial
import time

class OLEDDriver:
    """Python driver for Arduino Waveshare OLED with hardware IO support"""

    def __init__(self, port='/dev/tty.usbserial-0001', baudrate=115200, width=240, height=320):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)
        self.ser.reset_input_buffer()
        self.objects = []  
        self.init_screen(width, height)

    def init_screen(self, w, h):
        self.ser.write(b'I')
        self.ser.write(w.to_bytes(2, 'little'))
        self.ser.write(h.to_bytes(2, 'little'))
        self._wait_for_ack()

    def signal_win(self):
        self.ser.write(b'V')
        return self._wait_for_ack()

    def analog_read(self, pin):
        if self.ser.in_waiting > 0:
            self.ser.read(self.ser.in_waiting)
        self.ser.write(b'a')
        self.ser.write(bytes([pin]))
        res = self.ser.read(2)
        return int.from_bytes(res, 'little') if len(res) == 2 else 0

    def analog_write(self, pin, value):
        self.ser.write(b'A')
        self.ser.write(bytes([pin]))
        self.ser.write(value.to_bytes(2, 'little'))
        return self._wait_for_ack()

    def digital_read(self, pin):
        if self.ser.in_waiting > 0:
            self.ser.read(self.ser.in_waiting)
        self.ser.write(b'D')
        self.ser.write(bytes([pin]))
        start = time.time()
        while self.ser.in_waiting == 0:
            if time.time() - start > 0.1: return 0
        res = self.ser.read(1)
        return int.from_bytes(res, 'big')

    def digital_write(self, pin, state):
        self.ser.write(b'L')
        self.ser.write(bytes([pin, 1 if state else 0]))
        return self._wait_for_ack()

    # --- Screen Management & Drawing ---
    def clear(self):
        self.ser.write(b'C')
        self._wait_for_ack()
        self.objects = []

    def draw_rect(self, x, y, w, h, color=0):
        self.objects.append(('rect', x, y, w, h, color))

    def draw_circle(self, x, y, r, color=0):
        self.objects.append(('circle', x, y, r, color))

    def draw_triangle(self, x0, y0, x1, y1, x2, y2, color=0):
        self.objects.append(('triangle', x0, y0, x1, y1, x2, y2, color))

    def draw_wire(self, x, y, w=200, h=10, color=0):
        self.objects.append(('wire', x, y, w, h, color))

    def cut_wire(self, x, y, w=200, h=10):
        self.objects.append(('rect', x, y, w, h, 10))

    def draw_text(self, x, y, text, size=1, color=0):
        self.objects.append(('text', x, y, text, size, color))

    def update(self):
        self.ser.write(b'C')
        self._wait_for_ack()
        for obj in self.objects:
            if obj[0] == 'rect': self._send_rect(*obj[1:])
            elif obj[0] == 'circle': self._send_circle(*obj[1:])
            elif obj[0] == 'triangle': self._send_triangle(*obj[1:])
            elif obj[0] == 'wire': self._send_wire(*obj[1:])
            elif obj[0] == 'text': self._send_text(*obj[1:])

    # --- Private Serial Protocols ---
    def _wait_for_ack(self):
        start_time = time.time()
        while (time.time() - start_time) < 0.5:
            if self.ser.in_waiting > 0:
                res = self.ser.read(1)
                if res == b'K':
                    return True
        return False

    def _send_rect(self, x, y, w, h, color):
        self.ser.write(b'R'); [self.ser.write(v.to_bytes(2,'little')) for v in [x,y,w,h]]
        self.ser.write(bytes([color])); self._wait_for_ack()

    def _send_circle(self, x, y, r, color):
        self.ser.write(b'O'); [self.ser.write(v.to_bytes(2,'little')) for v in [x,y,r]]
        self.ser.write(bytes([color])); self._wait_for_ack()

    def _send_triangle(self, x0, y0, x1, y1, x2, y2, color):
        self.ser.write(b'G'); [self.ser.write(v.to_bytes(2,'little')) for v in [x0,y0,x1,y1,x2,y2]]
        self.ser.write(bytes([color])); self._wait_for_ack()

    def _send_wire(self, x, y, w, h, color):
        self.ser.write(b'W'); [self.ser.write(v.to_bytes(2,'little')) for v in [x,y,w,h]]
        self.ser.write(bytes([color])); self._wait_for_ack()

    def _send_text(self, x, y, text, size, color):
        self.ser.write(b'T'); [self.ser.write(v.to_bytes(2,'little')) for v in [x,y]]
        self.ser.write(bytes([size, color, len(text)])); self.ser.write(text.encode()); self._wait_for_ack()