import sys
import time
from mazes import MazeGame
from wires import WiresGame
from LCDDriver import LCDDriver

# --- CONFIG ---
SERIAL_PORT = '/dev/tty.usbserial-0001'

def main():
    maze_driver = LCDDriver(port=SERIAL_PORT)
    time.sleep(0.5) # Give it a moment to sync

    pin_start = 14
    if maze_driver.digital_read(pin_start):
        print("--- BOMB ARMED ---")
        
        # 1. Start the Maze
        print("Initializing Module 1: The Maze...")
        
        # --- THE FIX: Create the driver object first ---

        
        # Now pass the DRIVER object, not the PORT string
        maze_instance = MazeGame(maze_driver)
        
        # Run the maze and wait for "win"
        maze_status = maze_instance.run()

        if maze_status == "win":
            print("\n[✔] MAZE SOLVED!")
            
            # Close the connection so the next module can reset the hardware
            maze_instance.lcd.ser.close() 
            print("Resetting hardware... Please wait 2 seconds.")
            time.sleep(2.0) 
            
            print("Loading Module 2: The Wires...")
        else:
            print("\n[!] MAZE FAILED.")
            sys.exit()

        # 2. Start the Wires
        try:
            # Create a fresh driver for the Wires
            wire_driver = LCDDriver(port=SERIAL_PORT)
            time.sleep(0.5) 

            wire_driver.digital_write(15, 1)
            
            wires_instance = WiresGame(wire_driver)
            
            # Run the wires and wait for "win" or "lose"
            wires_status = wires_instance.run()

            if wires_status == "win":
                print("\n" + "="*30)
                print("  BOMB DEFUSED!  ")
                print("  YOU SURVIVED!  ")
                print("="*30)
            else:
                print("\n[!] BOOM!")
                sys.exit()
                
        except Exception as e:
            print(f"Serial Error: {e}")
            sys.exit()

if __name__ == "__main__":
    main()