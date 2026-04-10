from engi1020.arduino.api import *
import asyncio
import time

POT_PIN = 3 # 4D13
CLK_PIN = 3
DIO_PIN = 2
TICK_PIN = 5

MAX_TIME = 600
STABLE_THRESHOLD = 20
STABLE_TIME = 3

def pot_to_time(value):
    """
    Convert potentiometer (0–1023) to time in seconds
    """
    return int((value / 1023) * MAX_TIME)


def display_time(seconds):
    """
    Show time on 7-segmented display
    """
    minutes = seconds // 60
    secs = seconds % 60
    display_value = minutes * 100 + secs

    tm1637_write(CLK_PIN, DIO_PIN, display_value)


def select_time():
    """
    Blocking function.
    User turns potentiometer to select time.
    When it stops moving → returns selected time.
    """

    last_val = analog_read(POT_PIN)
    last_change_time = time.time()

    while True:
        val = analog_read(POT_PIN)

        seconds = pot_to_time(val)

        display_time(seconds)

        if abs(val - last_val) > STABLE_THRESHOLD:
            last_change_time = time.time()
            last_val = val

        if time.time() - last_change_time > STABLE_TIME:
            print(f"Selected time: {seconds} seconds")
            return seconds

        time.sleep(0.1)


async def run_timer(start_time, game_state):
    time_left = start_time

    while time_left >= 0 and not game_state["game_over"]:
        display_time(time_left)
        buzzer_note(TICK_PIN, 1200, 0.12)

        if time_left == 0:
            print("[TIMER] 💥 BOOM - time ran out")
            game_state["game_over"] = True
            game_state["exploded"] = True
            return "LOSE"

        await asyncio.sleep(1)
        time_left -= 1

    
if __name__ == "__main__":
    digital_write(4,False)
    async def test():
        print("Turn the potentiometer to choose a time...")
        
        # Select time
        start_time = select_time()

        print(f"Starting countdown from {start_time} seconds")

        # Run countdown
        await run_timer(start_time, False)

    asyncio.run(test())
    