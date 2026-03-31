import asyncio
import time
from engi1020.arduino.api import *

from timer_module import select_time, run_timer
from simon_says import SimonSays
from passwords import Passwords
from morse_code import MorseCode


# ---------------- PIN CONFIG ----------------
RELAY_1 = 4   # simon / next
RELAY_2 = 7   # passwords / next
RELAY_3 = 6   # morse / next grove kit

PARTNER_SIGNAL_OUT = 15
PARTNER_SIGNAL = 16


# ---------------- HELPERS ----------------
async def set_relay(pin, state):
    digital_write(pin, state)
    await asyncio.sleep(0.5)


async def wait_for_partner_result():
    """
    Wait for one pulse = WIN
    Wait for second pulse within 2 sec = LOSE
    """
    print("Waiting for partner board result...")

    # wait for first pulse
    while not digital_read(PARTNER_SIGNAL):
        await asyncio.sleep(0.05)

    print("Pulse 1 detected")
    await asyncio.sleep(0.3)

    start = time.time()

    while time.time() - start < 2:
        if digital_read(PARTNER_SIGNAL):
            print("Pulse 2 detected -> LOSE")
            return "LOSE"
        await asyncio.sleep(0.05)

    print("Single pulse -> WIN")
    return "WIN"


# ---------------- MAIN GAME ----------------
async def main():
    print("Select time with potentiometer...")
    start_time = select_time()

    timer_task = asyncio.create_task(run_timer(start_time))

    try:
        # =====================================
        # SIMON SAYS
        # =====================================
        print("Running Simon Says")
        await set_relay(RELAY_1, False)

        # simon = SimonSays(2, 8, 9, 10, 11, 12, 13, 14, 15)

        # round_num = 0
        # strikes = 0
        # colour_sequence = []
        # first_time = True

        # while strikes < 3:
        #     simon.start(
        #         initial_round=round_num,
        #         initial_strikes=strikes,
        #         initial_colours=colour_sequence
        #     )

        #     if first_time:
        #         await simon.increase_round()
        #         first_time = False

        #     result = await simon.play()

        #     if result == "WIN":
        #         print("Simon solved")
        #         break

        #     elif result == "Lose":
        #         print("Simon failed")
        #         return

        #     round_num, strikes, colour_sequence = result

        # if strikes >= 3:
        #     print("BOOM - Too many Simon strikes")
        #     return

        # =====================================
        # PASSWORDS
        # =====================================
        print("Running Passwords")
        await set_relay(RELAY_1, True)
        await set_relay(RELAY_2, False)

        password_game = Passwords(8, 9, 10)

        password_result = await asyncio.to_thread(password_game.game_loop)

        if password_result != "WIN":
            print("BOOM - Passwords failed")
            return

        print("Passwords solved")

        # =====================================
        # MORSE CODE
        # =====================================
        print("Running Morse Code")
        await set_relay(RELAY_2, True)
        await set_relay(RELAY_3, False)

        morse_game = MorseCode(11, 12, 13)
        morse_game.start(0)

        morse_result = await morse_game.main()

        if morse_result != "WIN":
            print("BOOM - Morse failed")
            return

        print("Morse solved")

        # =====================================
        # PARTNER BOARD
        # =====================================
        print("Starting partner board")
        await set_relay(RELAY_3, True)

        digital_write(PARTNER_SIGNAL_OUT, True)
        await asyncio.sleep(0.5)
        digital_write(PARTNER_SIGNAL_OUT, False)

        partner_result = await wait_for_partner_result()

        if partner_result == "LOSE":
            print("BOOM - Partner failed")
            return

        print("🎉 CONGRATULATIONS - BOMB DEFUSED 🎉")

    finally:
        timer_task.cancel()
        try:
            await timer_task
        except:
            pass


if __name__ == "__main__":
    asyncio.run(main())
