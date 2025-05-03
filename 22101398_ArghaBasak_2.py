from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import sys

WIDTH, HEIGHT = 1000, 600

gem_size = 18
gem_fall_speed = 1

catcher_x = WIDTH // 2
catcher_y = 60
catcher_w = 120
catcher_h = 10

active_gem = None
score = 0
game_paused = False
game_over = False

BUTTON_SIZE = 30

def random_bright_color():
    return (
        random.uniform(0.5, 1.0),
        random.uniform(0.5, 1.0),  # 0.5 - 1, not too dark
        random.uniform(0.5, 1.0)
    )

def spawn_gem():
    return {
        "x": random.randint(gem_size, WIDTH - gem_size),
        "y": HEIGHT - gem_size,
        "color": random_bright_color()
    }

def draw_pixel(x, y):
    glBegin(GL_POINTS)
    glVertex2i(int(round(x)), int(round(y)))
    glEnd()

# Midpoint Line Drawing and 8-way Symmetry Section 

def find_zone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    abs_dx = abs(dx)
    abs_dy = abs(dy)
    if abs_dx >= abs_dy:
        if dx >= 0 and dy >= 0: return 0
        elif dx < 0 and dy >= 0: return 3
        elif dx < 0 and dy < 0: return 4
        else: return 7
    else:
        if dx >= 0 and dy >= 0: return 1
        elif dx < 0 and dy >= 0: return 2
        elif dx < 0 and dy < 0: return 5
        else: return 6

def to_zone0(x, y, zone):
    mapping = [
        (x, y), (y, x), (y, -x), (-x, y),
        (-x, -y), (-y, -x), (-y, x), (x, -y)
    ]
    return mapping[zone]

def from_zone0(x, y, zone):
    reverse = [
        (x, y), (y, x), (-y, x), (-x, y),
        (-x, -y), (-y, -x), (y, -x), (x, -y)
    ]
    return reverse[zone]

def midpoint_line(x1, y1, x2, y2):
    x1, y1, x2, y2 = round(x1), round(y1), round(x2), round(y2)
    zone = find_zone(x1, y1, x2, y2)
    zx1, zy1 = to_zone0(x1, y1, zone)
    zx2, zy2 = to_zone0(x2, y2, zone)
    zx1, zy1, zx2, zy2 = int(zx1), int(zy1), int(zx2), int(zy2)
    dx = zx2 - zx1
    dy = zy2 - zy1
    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * (dy - dx)
    x, y = zx1, zy1
    for _ in range(int(dx) + 1):
        px, py = from_zone0(x, y, zone)
        draw_pixel(px, py)
        if d > 0:
            y += 1
            d += incNE
        else:
            d += incE
        x += 1

# -------------------------------------------------------

def render_gem(cx, cy, r):                    # Creates the shape of gem
    midpoint_line(cx, cy + r, cx + r, cy)
    midpoint_line(cx + r, cy, cx, cy - r)
    midpoint_line(cx, cy - r, cx - r, cy)
    midpoint_line(cx - r, cy, cx, cy + r)

def check_aabb_overlap(a, b):
    return (
        a["x"] < b["x"] + b["width"] and
        a["x"] + a["width"] > b["x"] and
        a["y"] < b["y"] + b["height"] and
        a["y"] + a["height"] > b["y"]
    )

def render_catcher(x, y, w, h):
    glColor3f(1.0, 0.0, 0.0) if game_over else glColor3f(1.0, 1.0, 1.0)
    margin = 10                   # For V shape to make it look inward
    bl_x = x + margin
    br_x = x + w - margin
    b_y = y
    tl_x = x
    tr_x = x + w
    t_y = y + h
    midpoint_line(tl_x, t_y, tr_x, t_y)
    midpoint_line(tr_x, t_y, br_x, b_y)
    midpoint_line(br_x, b_y, bl_x, b_y)
    midpoint_line(bl_x, b_y, tl_x, t_y)

def render_ui_controls():                    #Creating Restart Play Exit button
    glColor3f(0.0, 1.0, 1.0)                 #BLUE GREEN
    x_start = 20
    y_center = HEIGHT - 20 - BUTTON_SIZE // 2
    midpoint_line(x_start, y_center, x_start + BUTTON_SIZE, y_center)
    midpoint_line(x_start, y_center, x_start + 10, y_center + 10)
    midpoint_line(x_start, y_center, x_start + 10, y_center - 10)

    glColor3f(1.0, 0.6, 0.0)                 #ORANGE
    cx = WIDTH // 2
    top_y = HEIGHT - 20
    bot_y = HEIGHT - 20 - BUTTON_SIZE
    if game_paused:
        midpoint_line(cx - 5, bot_y, cx - 5, top_y)
        midpoint_line(cx - 5, top_y, cx + 10, (top_y + bot_y) // 2)
        midpoint_line(cx + 10, (top_y + bot_y) // 2, cx - 5, bot_y)
    else:
        midpoint_line(cx - 8, bot_y, cx - 8, top_y)
        midpoint_line(cx + 8, bot_y, cx + 8, top_y)

    glColor3f(1.0, 0.0, 0.0)                 #RED
    midpoint_line(WIDTH - 20 - BUTTON_SIZE, HEIGHT - 20,
                  WIDTH - 20, HEIGHT - 20 - BUTTON_SIZE)
    midpoint_line(WIDTH - 20 - BUTTON_SIZE, HEIGHT - 20 - BUTTON_SIZE,
                  WIDTH - 20, HEIGHT - 20)

def render_frame():                         #Main display function
    glClear(GL_COLOR_BUFFER_BIT)
    render_catcher(catcher_x, catcher_y, catcher_w, catcher_h)
    render_ui_controls()
    if active_gem:
        glColor3f(*active_gem["color"])
        render_gem(active_gem["x"], active_gem["y"], gem_size)
    glutSwapBuffers()                       # For visibility

def game_loop(value):
    global active_gem, score, game_paused, gem_fall_speed, game_over
    if game_paused:
        glutPostRedisplay()                 # Redraw the display
        glutTimerFunc(16, game_loop, 0)
        return

    if active_gem:
        active_gem["y"] -= gem_fall_speed
        gem_box = {
            "x": active_gem["x"] - gem_size,
            "y": active_gem["y"] - gem_size,       # Creates a bounding box for gem
            "width": 2 * gem_size,
            "height": 2 * gem_size
        }
        catcher_box = {
            "x": catcher_x,
            "y": catcher_y,                        # Creates a bounding box for catcher
            "width": catcher_w,
            "height": catcher_h
        }
        if check_aabb_overlap(gem_box, catcher_box):
            score += 1
            gem_fall_speed += 0.2
            print(f"Gem caught! Score: {score}, Speed: {gem_fall_speed:.2f}")
            active_gem = spawn_gem()
        elif active_gem["y"] < 0:
            print(f"Game Over! Final Score: {score}")
            active_gem = None
            game_paused = True
            game_over = True

    glutPostRedisplay()
    glutTimerFunc(16, game_loop, 0)

def handle_keys(key, x, y):             #Catcher from left to right
    global catcher_x
    if game_paused: return
    if key == GLUT_KEY_LEFT and catcher_x > 0:
        catcher_x -= 10
    elif key == GLUT_KEY_RIGHT and catcher_x + catcher_w < WIDTH:
        catcher_x += 10

def handle_mouse(button, state, x, y):
    global game_paused, score, gem_fall_speed, active_gem, game_over
    if state != GLUT_DOWN:
        return
    y = HEIGHT - y
    if 20 <= x <= 20 + BUTTON_SIZE and HEIGHT - 20 - BUTTON_SIZE <= y <= HEIGHT - 20:
        score = 0
        gem_fall_speed = 2
        active_gem = spawn_gem()            
        game_paused = False
        game_over = False
        print("Restarting:")

    if WIDTH // 2 - 15 <= x <= WIDTH // 2 + 15 and HEIGHT - 20 - BUTTON_SIZE <= y <= HEIGHT - 20:
        game_paused = not game_paused

    if WIDTH - 20 - BUTTON_SIZE <= x <= WIDTH - 20 and HEIGHT - 20 - BUTTON_SIZE <= y <= HEIGHT - 20:
        print(f"Goodbye! Final Score: {score}")
        try:
            glutLeaveMainLoop()
        except:
            sys.exit()

def init_canvas():
    glClearColor(0.0, 0.0, 0.0, 0.0)
   # glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)

def start_game():
    global active_gem
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"My Unique Catch the Gems Game")
    init_canvas()
    active_gem = spawn_gem()
    glutDisplayFunc(render_frame)
    glutMouseFunc(handle_mouse)
    glutSpecialFunc(handle_keys)
    glutTimerFunc(16, game_loop, 0)
    glutMainLoop()

if __name__ == "__main__":
    start_game()
