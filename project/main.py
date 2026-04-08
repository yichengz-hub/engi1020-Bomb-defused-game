import asyncio
import time
from engi1020.arduino.api import *

from timer_module import select_time, run_timer
from simon_says import SimonSays
from passwords import Passwords
from morse_code import MorseCode


# ---------------- PIN CONFIG ----------------
SIMON_RELAY = 4
PASSWORD_RELAY = 6
MORSE_RELAY = 7
PARTNER_SIGNAL = 16

WIN = "WIN"
LOSE = "LOSE"


# ---------------- HELPERS ----------------
async def run_password_async(game):
    return await asyncio.to_thread(game.game_loop)

async def set_relay(pin, state):
    print(f"[RELAY] Pin {pin} -> {'HIGH' if state else 'LOW'}")
    digital_write(pin, state)
    await asyncio.sleep(0.5)

async def bomb_explode_melody():
    """
    Sad descending explosion melody on Grove buzzer D5
    """
    notes = [880, 740, 622, 523, 440, 330]

    for note in notes:
        buzzer_note(5, note, 0.25)
        await asyncio.sleep(0.28)

    # final dramatic low tone
    buzzer_note(5, 220, 0.8)
    await asyncio.sleep(0.9)

async def initialize_relays():
    """
    Active LOW relays:
    True = OFF
    False = ON
    """
    print("[SYSTEM] Initializing all relays OFF")
    digital_write(SIMON_RELAY, True)
    digital_write(PASSWORD_RELAY, True)
    digital_write(MORSE_RELAY, True)
    await asyncio.sleep(0.5)


async def wait_for_partner_result():
    print("[PARTNER] Waiting for partner board result...")

    while not digital_read(PARTNER_SIGNAL):
        await asyncio.sleep(0.05)

    print("[PARTNER] Pulse 1 detected")
    await asyncio.sleep(0.3)

    start = time.time()

    while time.time() - start < 2:
        if digital_read(PARTNER_SIGNAL):
            print("[PARTNER] Pulse 2 detected -> LOSE")
            return LOSE
        await asyncio.sleep(0.05)

    print("[PARTNER] Single pulse -> WIN")
    return WIN


async def check_explosion(game_state):
    while True:
        if game_state["exploded"]:
            print("[TIMER] 💥 BOMB EXPLODED")
            return LOSE
        await asyncio.sleep(0.05)


async def run_with_bomb_watch(module_coro, game_state):
    module_task = asyncio.create_task(module_coro)

    while not module_task.done():
        if game_state["game_over"]:
            print("[SYSTEM] Timer expired -> ending module")
            module_task.cancel()
            return "LOSE"

        await asyncio.sleep(0.05)

    return await module_task


async def password_game_async(game):
    while True:
        result = game.game_loop()

        if result is not None:
            return result

        await asyncio.sleep(0.01)


async def clear_password_inputs():
    print("[PASSWORD] Clearing stale button states...")

    while (
        digital_read(8) or
        digital_read(9) or
        digital_read(10)
    ):
        print(
            f"[PASSWORD] waiting clear: "
            f"8={digital_read(8)} "
            f"9={digital_read(9)} "
            f"10={digital_read(10)}"
        )
        await asyncio.sleep(0.02)

    await asyncio.sleep(0.2)
    print("[PASSWORD] Pins clear")


# ---------------- MAIN GAME ----------------
async def main():
    game_state = {"game_over": False, "exploded": False}

    print("[SYSTEM] Select time with potentiometer...")
    start_time = select_time()

    await initialize_relays()

    timer_task = asyncio.create_task(run_timer(start_time, game_state))

    try:
        # =====================================
        # SIMON SAYS
        # =====================================
        print("\n[SYSTEM] Running Simon Says")
        await set_relay(SIMON_RELAY, False)

        simon = SimonSays(4, 8, 9, 10, 11, 12, 13, 14, 15)

        round_num = 0
        strikes = 0
        colour_sequence = []
        first_time = True

        while strikes < 3:
            if game_state["exploded"]:
                print("[SYSTEM] 💥 BOOM")
                await bomb_explode_melody()
                return

            print(f"[SIMON] Round={round_num}, Strikes={strikes}")
            print(f"[SIMON] Previous sequence = {colour_sequence}")

            simon.start(
                initial_round=round_num,
                initial_strikes=strikes,
                initial_colours=colour_sequence.copy()
            )

            if first_time:
                await simon.increase_round()
                first_time = False

            result = await run_with_bomb_watch(
                simon.play(),
                game_state
            )

            if result == WIN:
                print("[SIMON] Solved")
                break

            if result == LOSE:
                print("[SIMON] Failed")
                return

            round_num, strikes, colour_sequence = result

            print(f"[SIMON] Updated sequence = {colour_sequence}")
            print(f"[SIMON] Strikes = {strikes}")

        if strikes >= 3:
            print("[SYSTEM] BOOM - Too many Simon strikes")
            await bomb_explode_melody()
            return

        # =====================================
        # PASSWORDS
        # =====================================
        print("\n[SYSTEM] Simon complete")
        await asyncio.sleep(1)

        print("[SYSTEM] Switching to Passwords")
        await set_relay(SIMON_RELAY, True)
        await set_relay(PASSWORD_RELAY, False)

        print("[SYSTEM] Waiting for relay and pins to settle...")
        await asyncio.sleep(0.5)

        print("[SIMON] Stopping buzzer + clearing pins")
        buzzer_stop(8)
        digital_write(8, False)
        digital_write(9, False)
        digital_write(10, False)

        await clear_password_inputs()

        print("\n[SYSTEM] Running Passwords")
        password_game = Passwords(8, 9, 10)

        password_result = await run_with_bomb_watch(
            password_game.game_loop(),
            game_state
        )

        if password_result != WIN:
            print("[SYSTEM] 💥 BOOM - Passwords failed")
            await bomb_explode_melody()
            return

        print("[PASSWORD] Solved")

        # =====================================
        # MORSE CODE
        # =====================================
        print("\n[SYSTEM] Running Morse Code")
        await set_relay(PASSWORD_RELAY, True)
        await set_relay(MORSE_RELAY, False)

        digital_write(11, False)
        digital_write(12, False)

        morse_game = MorseCode(11, 12, 10)
        morse_game.start(0)

        morse_result = await run_with_bomb_watch(
            morse_game.main(),
            game_state
        )

        if morse_result != WIN:
            print("[SYSTEM] 💥 BOOM - Morse failed")
            await bomb_explode_melody()
            return

        print("[MORSE] Solved")

        # =====================================
        # PARTNER BOARD
        # =====================================
        # print("\n[SYSTEM] Starting partner board")
        # await set_relay(MORSE_RELAY, True)

        # digital_write(PARTNER_SIGNAL, True)
        # await asyncio.sleep(0.5)
        # digital_write(PARTNER_SIGNAL, False)

        # partner_result = await run_with_bomb_watch(
        #     wait_for_partner_result(),
        #     game_state
        # )

        # if partner_result == LOSE:
        #     print("[SYSTEM] 💥 BOOM - Partner failed")
        #     return

        print("\n🎉 CONGRATULATIONS - BOMB DEFUSED 🎉")

    finally:
        print("[SYSTEM] Cleaning up timer task")
        timer_task.cancel()
        try:
            await timer_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(main())
