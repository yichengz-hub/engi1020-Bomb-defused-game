import time, sys
from OLEDDriver import OLEDDriver
from mazes import MazeGame
from wires import WiresGame

# CONFIG: Bridging Pin 16 (Sender) to Pin 17 (Receiver)
SIGNAL_OUT = 16 
SIGNAL_IN  = 17 
RELAY_PIN  = 6

def main():
    try:
        driver = OLEDDriver()
        
        # 1. Start Trigger (Digital)
        print(f"[WAITING] Pulse Pin {SIGNAL_IN} HIGH to start...")
        while driver.digital_read(SIGNAL_IN) == 0:
            time.sleep(0.1)

        # 2. Game Sequence
        driver.digital_write(RELAY_PIN, 0)
        driver.init_screen(240, 280)
        if MazeGame(driver).run() == "win":
            time.sleep(1)
            driver.digital_write(RELAY_PIN, 1)
            driver.init_screen(240, 320)
            result = WiresGame(driver).run()
            
            # 3. Signaling Result (Analog)
            if result == "win":
                print("[WIN] Sending 1000")
                driver.digital_write(SIGNAL_IN, 0)
                driver.analog_write(SIGNAL_OUT, 1000)
            else:
                print("[LOSS] Sending 500")
                driver.analog_write(SIGNAL_OUT, 500)

            # 4. Monitoring Loop
            while True:
                if result == "win":
                    print("[WIN] Sending 1000")
                    driver.digital_read(SIGNAL_IN, 1)
                else:
                    print("[LOSS] Sending 500")
                    driver.analog_write(SIGNAL_OUT, 500)

                val = driver.analog_read(SIGNAL_IN)
                print(f"Voltage on A3: {val}")
                time.sleep(0.5)

    except KeyboardInterrupt:
        sys.exit()

if __name__ == "__main__":
    main()