from engi1020.arduino.api import *
import time


def countdown_test(start_seconds=300):
    """
    Countdown test for TM1637 display using firmware-level command.
    Displays time as MMSS.
    """

    time_left = start_seconds

    while time_left >= 0:
        minutes = time_left // 60
        seconds = time_left % 60

        # Convert to MMSS format
        display_value = minutes * 100 + seconds

        # NEW fast firmware function
        tm1637_write(3, 2, display_value)

        print(f"Displaying: {minutes:02}:{seconds:02}")

        if time_left == 0:
            print("KABOOM!")
            break

        time.sleep(1)
        time_left -= 1


# if __name__ == "__main__":
#     countdown_test()

while True:
    val = analog_read(1)
    print(val)
    time.sleep(0.2)
    