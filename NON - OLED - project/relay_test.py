from engi1020.arduino.api import *
import time

# Pin 2 corresponds to Port D2 on the Grove Shield
RELAY_PIN = 2

def relay_test():
    print("--- Relay Test Starting ---")
    print("You should hear a physical 'CLICK' every 2 seconds.")
    
    try:
        while True:
            # Turn Relay ON (Close the circuit)
            print("Relay: ON (Closed)")
            digital_write(RELAY_PIN, True)
            time.sleep(2)
            
            # Turn Relay OFF (Open the circuit)
            print("Relay: OFF (Open)")
            digital_write(RELAY_PIN, False)
            time.sleep(2)
            
    except KeyboardInterrupt:
        # Safety: Turn off the relay if you stop the script (Ctrl+C)
        digital_write(RELAY_PIN, False)
        print("\nTest Stopped. Relay reset to OFF.")

# Run the test
relay_test()