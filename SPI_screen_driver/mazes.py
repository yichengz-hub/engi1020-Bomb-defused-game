import time
import random
from LCDDriver import LCDDriver

class MazeGame:
    def __init__(self, port='/dev/tty.usbserial-0001', width=240, height=280):
        self.lcd = LCDDriver(port, width=width, height=height)
        
        # --- COLOR PALETTE ---
        self.BG_COL = 10     # Black
        self.DOT_COL = 0     # White
        self.PLAYER_COL = 1  # Red
        self.MARKER_COL = 2  # Green
        self.GOAL_COL = 0    # White (Goal Square)
        
        self.GRID_STEP = 40
        self.OFFSET_X, self.OFFSET_Y = 20, 40
        self.SIZE = 7

        # Button Pin Mapping
        self.PIN_UP = 2
        self.PIN_DOWN = 3
        self.PIN_LEFT = 4
        self.PIN_RIGHT = 5
        self.PIN_RESET = 6

        self.MAZES = [
            {"id": 1, "markers": [(0,1), (5,2)], "walls": ["h10", "h12", "h13", "h14", "h21", "h23", "h33", "h43", "h42", "h41", "h40", "h50", "h31", "h44", "v01", "v02", "v03", "v15", "v24", "v35", "v44", "v33", "v22", "v21", "v20"]},
            {"id": 2, "markers": [(1,3), (4,1)], "walls": ["h00", "h20", "h50", "h11", "h31", "h41", "h22", "h42", "h13", "h33", "h44", "v20", "v11", "v02", "v31", "v22", "v13", "v14", "v04", "v05", "v43", "v44", "v33", "v24", "v25"]},
            {"id": 3, "markers": [(3,3), (5,3)], "walls": ["h01", "h10", "h31", "h41", "h14", "h24", "v01", "v11", "v12", "v13", "v03", "v04", "v20", "v21", "v22", "v23", "v24", "v30", "V32", "v33", "v34", "v35", "v41", "v42", "v43", "v44"]},
            {"id": 4, "markers": [(0,0), (0,3)], "walls": ["h12", "h22", "h42", "h13", "h23", "h33", "h43", "h31", "h41", "h20", "h30", "h40", "h14", "h24", "h34", "v01", "v02", "v03", "v10", "v11", "v22", "v42", "v44", "v45", "v25"]},
            {"id": 5, "markers": [(4,2), (3,5)], "walls": ["h00", "h10", "h20", "h30", "h11", "h21", "h41", "h51", "h22", "h32", "h13", "h23", "h43", "h24", "h34", "h44", "v41", "v12", "v32", "v33", "v43", "v44", "v03", "v04", "v05"]},
            {"id": 6, "markers": [(4,0), (2,4)], "walls": ["h30", "h12", "h22", "h41", "h14", "h24", "h03", "h44", "h52", "v00", "v01", "v11", "v12", "v13", "v14", "v24", "v22", "v21", "v20", "v32", "v33", "v34", "v35", "v41", "v43"]},
            {"id": 7, "markers": [(1,0), (1,5)], "walls": ["h10", "h20", "h21", "h31", "h41", "h02", "h12", "h32", "h52", "h33", "h43", "h14", "h24", "h34", "v01", "v04", "v12", "v13", "v14", "v21", "v30", "v32", "v41", "v43", "v44"]},
            {"id": 8, "markers": [(3,0), (2,3)], "walls": ["h20", "h11", "h21", "h31", "h41", "h22", "h32", "h33", "h43", "h53", "h24", "h34", "h44", "h54", "h13", "v00", "v30", "v21", "v41", "v02", "v42", "v03", "v23", "v04", "v14"]},
            {"id": 9, "markers": [(2,1), (0,4)], "walls": ["h20", "h30", "h31", "h22", "h12", "h33", "h43", "h42", "h54", "v00", "v01", "v11", "v31", "v41", "v42", "v33", "v22", "v03", "v04", "v13", "v14", "v15", "v44", "v24", "v35"]}
        ]

        self.state = {"gx": 0, "gy": 0, "tx": 0, "ty": 0, "facing": 'w', "maze": None}
        self.game_over = False  # Flag to track if the goal was reached
        self.lcd.init_screen(width, height)
        self.init_game()

    def _get_coords(self, tx, ty):
        return self.OFFSET_X + (tx * self.GRID_STEP), self.OFFSET_Y + (ty * self.GRID_STEP)

    def _draw_player(self, tx, ty, color, direction):
        sx, sy = self._get_coords(tx, ty)
        s = self.SIZE
        if direction == 'w': self.lcd._send_triangle(sx, sy-s, sx-s, sy+s, sx+s, sy+s, color)
        elif direction == 's': self.lcd._send_triangle(sx, sy+s, sx-s, sy-s, sx+s, sy-s, color)
        elif direction == 'a': self.lcd._send_triangle(sx-s, sy, sx+s, sy-s, sx+s, sy+s, color)
        elif direction == 'd': self.lcd._send_triangle(sx+s, sy, sx-s, sy-s, sx-s, sy+s, color)

    def _draw_marker(self, tx, ty, color):
        sx, sy = self._get_coords(tx, ty)
        self.lcd._send_rect(sx-7, sy-7, 14, 2, color)
        self.lcd._send_rect(sx-7, sy+5, 14, 2, color)
        self.lcd._send_rect(sx-7, sy-7, 2, 14, color)
        self.lcd._send_rect(sx+5, sy-7, 2, 14, color)

    def _draw_goal(self, tx, ty, color):
        sx, sy = self._get_coords(tx, ty)
        self.lcd._send_rect(sx-4, sy-4, 8, 8, color)

    def _erase_at(self, tx, ty):
        sx, sy = self._get_coords(tx, ty)
        self.lcd._send_rect(sx-10, sy-10, 20, 20, self.BG_COL)
        self.lcd._send_rect(sx-1, sy-1, 2, 2, self.DOT_COL)
        if (tx, ty) in self.state["maze"]['markers']:
            self._draw_marker(tx, ty, self.MARKER_COL)
        if tx == self.state["tx"] and ty == self.state["ty"]:
            self._draw_goal(tx, ty, self.GOAL_COL)

    def init_game(self):
        self.game_over = False
        self.lcd.clear()
        self.state["maze"] = random.choice(self.MAZES)
        
        for ix in range(6):
            for iy in range(6):
                sx, sy = self._get_coords(ix, iy)
                self.lcd._send_rect(sx-1, sy-1, 2, 2, self.DOT_COL)
        
        all_dots = [(x,y) for x in range(6) for y in range(6)]
        self.state["tx"], self.state["ty"] = random.choice(all_dots)
        
        possible = [d for d in all_dots if (abs(d[0]-self.state["tx"]) + abs(d[1]-self.state["ty"])) >= 4]
        self.state["gx"], self.state["gy"] = random.choice(possible)
        self.state["facing"] = 'w'
        
        for cx, cy in self.state["maze"]['markers']:
            self._draw_marker(cx, cy, self.MARKER_COL)
        
        self._draw_goal(self.state["tx"], self.state["ty"], self.GOAL_COL)
        self._draw_player(self.state["gx"], self.state["gy"], self.PLAYER_COL, self.state["facing"])

    def move(self, direction):
        if self.game_over: return  # Ignore movements if game is finished

        nx, ny = self.state["gx"], self.state["gy"]
        if direction == 'w': ny -= 1
        elif direction == 's': ny += 1
        elif direction == 'a': nx -= 1
        elif direction == 'd': nx += 1
        else: return

        self.state["facing"] = direction
        is_valid = False
        
        if 0 <= nx <= 5 and 0 <= ny <= 5:
            wall = f"v{self.state['gx']}{self.state['gy']}" if nx > self.state['gx'] else f"v{nx}{ny}" if nx < self.state['gx'] else f"h{self.state['gx']}{self.state['gy']}" if ny > self.state['gy'] else f"h{nx}{ny}"
            if wall not in self.state["maze"]['walls']:
                is_valid = True
        
        if is_valid:
            self._erase_at(self.state["gx"], self.state["gy"])
            self.state["gx"], self.state["gy"] = nx, ny
            self._draw_player(self.state["gx"], self.state["gy"], self.PLAYER_COL, self.state["facing"])
            
            # CHECK FOR WIN CONDITION
            if self.state["gx"] == self.state["tx"] and self.state["gy"] == self.state["ty"]:
                self.game_over = True
                self.lcd.clear()
                self.lcd.draw_text(40, 100, "SOLVED!", size=4, color=self.MARKER_COL)
                self.lcd.draw_text(25, 160, "Press Reset to Play", size=2, color=0)
        else:
            # Re-draw to show orientation change
            self._erase_at(self.state["gx"], self.state["gy"])
            self._draw_player(self.state["gx"], self.state["gy"], self.PLAYER_COL, self.state["facing"])

    def run(self):
        """The main execution loop for hardware interaction."""
        print("Maze Game Running... Press hardware buttons to move.")
        try:
            while True:
                # Check Reset Button (Pin 6)
                # Note: Pullup means Pressed == 1
                if self.lcd.digital_read(self.PIN_RESET) == 1:
                    self.init_game()
                    time.sleep(0.5)

                # Check Directional Buttons (Pins 2-5)
                # Note: Pullup means Pressed == 1
                if self.lcd.digital_read(self.PIN_UP) == 1:
                    self.move('w')
                    time.sleep(0.15)
                elif self.lcd.digital_read(self.PIN_DOWN) == 1:
                    self.move('s')
                    time.sleep(0.15)
                elif self.lcd.digital_read(self.PIN_LEFT) == 1:
                    self.move('a')
                    time.sleep(0.15)
                elif self.lcd.digital_read(self.PIN_RIGHT) == 1:
                    self.move('d')
                    time.sleep(0.15)

                time.sleep(0.01)
        except KeyboardInterrupt:
            print("Game Stopped.")