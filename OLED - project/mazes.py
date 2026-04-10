import time
import random
from OLEDDriver import OLEDDriver

WHITE, RED, GREEN, BLUE, YELLOW, GREY, BLACK = 0, 1, 2, 3, 4, 5, 10

class MazeGame:
    def __init__(self, oled):
        self.oled = oled

        self.BG_COL = BLACK
        self.DOT_COL = WHITE
        self.PLAYER_COL = RED
        self.MARKER_COL = GREEN
        self.GOAL_COL = WHITE
        
        self.GRID_STEP = 35
        self.OFFSET_X, self.OFFSET_Y = 30, 50
        self.SIZE = 6

        self.PIN_UP = 2
        self.PIN_DOWN = 3
        self.PIN_LEFT = 4
        self.PIN_RIGHT = 5

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
        self.reset()

    def _get_coords(self, tx, ty):
        return self.OFFSET_X + (tx * self.GRID_STEP), self.OFFSET_Y + (ty * self.GRID_STEP)

    def _draw_player(self, tx, ty, color, direction):
        sx, sy = self._get_coords(tx, ty)
        s = self.SIZE
        if direction == 'w': self.oled._send_triangle(sx, sy-s, sx-s, sy+s, sx+s, sy+s, color)
        elif direction == 's': self.oled._send_triangle(sx, sy+s, sx-s, sy-s, sx+s, sy-s, color)
        elif direction == 'a': self.oled._send_triangle(sx-s, sy, sx+s, sy-s, sx+s, sy+s, color)
        elif direction == 'd': self.oled._send_triangle(sx+s, sy, sx-s, sy-s, sx-s, sy+s, color)

    def _draw_marker(self, tx, ty, color):
        sx, sy = self._get_coords(tx, ty)
        self.oled._send_rect(sx-7, sy-7, 14, 2, color)
        self.oled._send_rect(sx-7, sy+5, 14, 2, color)
        self.oled._send_rect(sx-7, sy-7, 2, 14, color)
        self.oled._send_rect(sx+5, sy-7, 2, 14, color)

    def _draw_goal(self, tx, ty, color):
        sx, sy = self._get_coords(tx, ty)
        self.oled._send_rect(sx-4, sy-4, 8, 8, color)

    def _erase_at(self, tx, ty):
        sx, sy = self._get_coords(tx, ty)
        self.oled._send_rect(sx-10, sy-10, 21, 21, self.BG_COL)
        self.oled._send_rect(sx-1, sy-1, 2, 2, self.DOT_COL)
        if (tx, ty) in self.state["maze"]['markers']:
            self._draw_marker(tx, ty, self.MARKER_COL)
        if tx == self.state["tx"] and ty == self.state["ty"]:
            self._draw_goal(tx, ty, self.GOAL_COL)

    def reset(self):
        self.oled.ser.write(b'C')
        time.sleep(0.1)
        self.state["maze"] = random.choice(self.MAZES)

        for ix in range(6):
            for iy in range(6):
                sx, sy = self._get_coords(ix, iy)
                self.oled._send_rect(sx-1, sy-1, 2, 2, self.DOT_COL)
        
        all_dots = [(x,y) for x in range(6) for y in range(6)]
        self.state["tx"], self.state["ty"] = random.choice(all_dots)

        possible = [d for d in all_dots if (abs(d[0]-self.state["tx"]) + abs(d[1]-self.state["ty"])) >= 3]
        self.state["gx"], self.state["gy"] = random.choice(possible)
        self.state["facing"] = 'w'
        
        for cx, cy in self.state["maze"]['markers']:
            self._draw_marker(cx, cy, self.MARKER_COL)
        
        self._draw_goal(self.state["tx"], self.state["ty"], self.GOAL_COL)
        self._draw_player(self.state["gx"], self.state["gy"], self.PLAYER_COL, self.state["facing"])

    def move(self, direction):
        nx, ny = self.state["gx"], self.state["gy"]
        if direction == 'w': ny -= 1
        elif direction == 's': ny += 1
        elif direction == 'a': nx -= 1
        elif direction == 'd': nx += 1

        self.state["facing"] = direction

        if not (0 <= nx <= 5 and 0 <= ny <= 5):
            return "collision"

        wall = f"v{self.state['gx']}{self.state['gy']}" if nx > self.state['gx'] else \
               f"v{nx}{ny}" if nx < self.state['gx'] else \
               f"h{self.state['gx']}{self.state['gy']}" if ny > self.state['gy'] else \
               f"h{nx}{ny}"
               
        if wall in self.state["maze"]['walls']:
            return "collision"

        self._erase_at(self.state["gx"], self.state["gy"])
        self.state["gx"], self.state["gy"] = nx, ny
        self._draw_player(self.state["gx"], self.state["gy"], self.PLAYER_COL, self.state["facing"])
        return "success"

    def run(self):
        print("Maze Active. Warning: Touching walls causes immediate failure.")
        last_states = {p: 0 for p in [self.PIN_UP, self.PIN_DOWN, self.PIN_LEFT, self.PIN_RIGHT]}
        
        while True:
            try:
                for pin, direction in zip([self.PIN_UP, self.PIN_DOWN, self.PIN_LEFT, self.PIN_RIGHT], ['w', 's', 'a', 'd']):
                    val = self.oled.digital_read(pin)
                    
                    if val == 1 and last_states[pin] == 0:
                        result = self.move(direction)

                        if result == "collision":
                            self.oled.ser.write(b'C')
                            time.sleep(0.1)
                            self.oled._send_text(40, 120, "GAME OVER", 2, RED)
                            time.sleep(2.0)
                            return "loss"

                        if self.state["gx"] == self.state["tx"] and self.state["gy"] == self.state["ty"]:
                            self.oled.ser.write(b'C')
                            time.sleep(0.1)
                            self.oled._send_text(40, 120, "MAZE SOLVED", 2, GREEN)
                            time.sleep(1.0)
                            return "win"
                            
                    last_states[pin] = val
                
                time.sleep(0.02)
            except Exception:
                self.oled.ser.reset_input_buffer()

if __name__ == "__main__":
    driver = OLEDDriver(port='/dev/tty.usbserial-0001')
    game = MazeGame(driver)
    final_result = game.run()
    print(f"Final Maze State: {final_result}")