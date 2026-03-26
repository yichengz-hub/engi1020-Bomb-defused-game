import time
from pynput import keyboard
from LCDDriver import LCDDriver

# Setup Driver
lcd = LCDDriver('/dev/tty.usbserial-0001', width=240, height=280)

# Game Config
PLAYER_COL, GOAL_COL, BG_COL = 3, 2, 10
STEP, SIZE = 5, 8
px, py = 25, 25
keys_pressed = set()

# Maze Walls (Invisible but solid)
walls = [
    [0, 0, 240, 5], [0, 275, 240, 5], [0, 0, 5, 280], [235, 0, 5, 280],
    [50, 50, 100, 10], [50, 50, 10, 80], [150, 100, 10, 80],
    [0, 180, 160, 10], [80, 220, 160, 10]
]
goal = [190, 240, 25, 25]

def on_press(key):
    try: keys_pressed.add(key.char.lower())
    except: pass
def on_release(key):
    try: keys_pressed.remove(key.char.lower())
    except: pass

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

def draw_player(x, y, color):
    lcd._send_triangle(x, y-SIZE, x-SIZE, y+SIZE, x+SIZE, y+SIZE, color)

def init_game():
    lcd.clear()
    lcd._send_rect(goal[0], goal[1], goal[2], goal[3], GOAL_COL)
    draw_player(px, py, PLAYER_COL)
    lcd.draw_text(10, 10, "BLIND MAZE", size=1, color=0)

def check_collision(nx, ny):
    if nx < 10 or nx > 230 or ny < 10 or ny > 270: return True
    for w in walls:
        if (nx+SIZE > w[0] and nx-SIZE < w[0]+w[2] and ny+SIZE > w[1] and ny-SIZE < w[1]+w[3]):
            return True
    return False

init_game()
print("Game Live! WASD to move. Press 'R' if you replug the screen.")

try:
    while True:
        # RESCUE LOGIC
        if 'r' in keys_pressed:
            lcd.init_screen(240, 280)
            init_game()
            time.sleep(0.5)
            continue

        nx, ny = px, py
        moved = False
        if 'w' in keys_pressed: ny -= STEP; moved = True
        if 's' in keys_pressed: ny += STEP; moved = True
        if 'a' in keys_pressed: nx -= STEP; moved = True
        if 'd' in keys_pressed: nx += STEP; moved = True

        if moved and not check_collision(nx, ny):
            draw_player(px, py, BG_COL) # Erase
            px, py = nx, ny
            draw_player(px, py, PLAYER_COL) # Draw
            
            if (px > goal[0] and px < goal[0]+goal[2] and py > goal[1] and py < goal[1]+goal[3]):
                lcd.clear()
                lcd.draw_text(40, 120, "YOU WIN!", size=3, color=2)
                time.sleep(2)
                px, py = 25, 25
                init_game()
        time.sleep(0.03)
except KeyboardInterrupt:
    listener.stop()