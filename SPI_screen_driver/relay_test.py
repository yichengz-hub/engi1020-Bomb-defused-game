import time
from SPI_screen_driver.OLEDDriver import LCDDriver

def main():
    lcd = LCDDriver(port='/dev/tty.usbserial-0001')
    RELAY_PIN = 16

    while True:

        lcd.digital_write(RELAY_PIN, 0)
        time.sleep(2)
        lcd.digital_write(RELAY_PIN, 1)
        time.sleep(2)

if __name__ == "__main__":
    main()