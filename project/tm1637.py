from engi1020.arduino.api import *

digits = [
    0x3f, 0x06, 0x5b, 0x4f,
    0x66, 0x6d, 0x7d, 0x07,
    0x7f, 0x6f
]


class TM1637:
    def __init__(self, clk, dio, brightness=7):
        self.clk = clk
        self.dio = dio
        self.brightness = brightness
        self._set_brightness()

    def clk_high(self):
        digital_write(self.clk, True)

    def clk_low(self):
        digital_write(self.clk, False)

    def dio_high(self):
        digital_write(self.dio, True)

    def dio_low(self):
        digital_write(self.dio, False)

    def start(self):
        self.dio_high()
        self.clk_high()
        self.dio_low()

    def stop(self):
        self.clk_low()
        self.dio_low()
        self.clk_high()
        self.dio_high()

    def write_byte(self, b):
        for i in range(8):
            self.clk_low()

            if (b >> i) & 1:
                self.dio_high()
            else:
                self.dio_low()

            self.clk_high()

        # ignore ACK for speed
        self.clk_low()
        self.clk_high()

    def _set_brightness(self):
        self.start()
        self.write_byte(0x88 | self.brightness)
        self.stop()

    def write(self, num):
        num = max(0, min(9999, num))

        d = [0, 0, 0, 0]

        for i in range(4):
            d[3 - i] = digits[num % 10]
            num //= 10

        self.start()
        self.write_byte(0x40)
        self.stop()

        self.start()
        self.write_byte(0xC0)

        for seg in d:
            self.write_byte(seg)

        self.stop()
        