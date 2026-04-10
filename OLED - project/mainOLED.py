import time, sys
from OLEDDriver import OLEDDriver
from mazes import MazeGame
from wires import WiresGame

# --- CONFIGURATION ---
SIGNAL_IN  = 16  # Handshake pin (Start trigger)
RESULT_LED = 15  # Result LED pin
RELAY_PIN  = 6   # Relay / Main Grove pin

def send_final_signal(driver, pin, seconds):
    """Sends a sustained HIGH pulse to notify the external system."""
    print(f"[SIGNAL] Pulsing Pin {pin} and {SIGNAL_IN} for {seconds}s")
    driver.digital_write(pin, 1)
    driver.digital_write(SIGNAL_IN, 1) # Send signal back on start pin too
    time.sleep(seconds)
    driver.digital_write(pin, 0)
    driver.digital_write(SIGNAL_IN, 0)
    print("[SIGNAL] Pulse complete.")

def main():
    try:
        # Initialize the hardware driver
        driver = OLEDDriver()
        
        # Initial cleanup
        driver.digital_write(RESULT_LED, 0)
        time.sleep(0.1)
        driver.ser.reset_input_buffer()

        # 1. DEBOUNCE WAIT LOOP (Starts game on clean signal)
        print(f"[WAITING] Pulse Pin {SIGNAL_IN} HIGH to start...")
        consecutive_highs = 0
        while consecutive_highs <= 1:
            if driver.digital_read(SIGNAL_IN):
                consecutive_highs += 1
                print(f"Signal detected... ({consecutive_highs}/3)")
            else:
                consecutive_highs = 0
            time.sleep(0.1)

        # 2. GAME STARTUP
        print("[START] Valid signal confirmed. Triggering Relay.")
        driver.digital_write(RELAY_PIN, 0) # Activate Relay (Active Low)
        driver.init_screen(240, 280)
        
        # Track victory across both games
        overall_winner = False

        # 3. RUN MAZE GAME,
        print("[GAME 1] Running Maze...")
        maze_result = MazeGame(driver).run()
        
        # Check Maze result (matches MazeGame "win"/"loss")
        if str(maze_result).strip().lower() == "win":
            print("[PROGRESS] Maze won! Moving to Wires...")
            time.sleep(1.0)
            
            # Reset hardware for second stage
            driver.digital_write(RELAY_PIN, 1) 
            driver.init_screen(240, 320)
            
            # 4. RUN WIRES GAME
            print("[GAME 2] Running Wires...")
            wires_result = WiresGame(driver).run()
            
            # Check Wires result (matches WiresGame "win"/"loss")
            if str(wires_result).strip().lower() == "win":
                overall_winner = True
            else:
                print("[STATUS] Wires failed.")
                overall_winner = False
        else:
            print("[STATUS] Maze failed.")
            overall_winner = False

        # --- 5. FINAL RESULT PHASE ---
        print("\n" + "="*30)
        print(f" FINAL RESULT: {'SUCCESS' if overall_winner else 'FAILURE'} ")
        print("="*30)

        # Synchronize Serial: Clear any leftover button-poll bytes
        time.sleep(0.2)
        driver.ser.reset_input_buffer()
        
        # Set Relay for final signaling
        driver.digital_write(RELAY_PIN, 0) 
        time.sleep(0.5) 

        if overall_winner:
            # Win Result: 2 Second Pulse
            send_final_signal(driver, RESULT_LED, 2)
        else:
            # Loss Result: 5 Second Pulse
            send_final_signal(driver, RESULT_LED, 5)

        print("[IDLE] Game sequence complete. System IDLE.")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nShutdown requested by user.")
        sys.exit()
    except Exception as e:
        print(f"\n[CRITICAL ERROR] {e}")
        sys.exit()

if __name__ == "__main__":
    main()