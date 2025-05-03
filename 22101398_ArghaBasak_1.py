import sys
import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


window_width = 800  # Initial window dimensions
window_height = 600  # Initial window dimensions
rain_positions = [{'x': random.uniform(-1, 1), 'y': random.uniform(0, 1)} for _ in range(100)]  # Random raindrop positions
rain_dx = 0.0  # Rain horizontal speed
rain_fall_speed = 0.01  # Rain falling speed
background_color = [0.3, 0.3, 0.3]  # Initial night color
is_daytime = False  # Day/Night toggle


def render_triangle(vertices, color):
    glColor3f(*color)
    glBegin(GL_TRIANGLES)
    for vertex in vertices:
        glVertex2f(*vertex)
    glEnd()


def render_house():
    # Draw the roof
    render_triangle([(-0.4, 0.0), (0.4, 0.0), (0.0, 0.5)], (0.8, 0.3, 0.3))

    # Draw the body
    render_triangle([(-0.3, 0.0), (0.3, 0.0), (-0.3, -0.5)], (0.6, 0.4, 0.3))
    render_triangle([(-0.3, -0.5), (0.3, -0.5), (0.3, 0.0)], (0.6, 0.4, 0.3))

    # Draw the door with GL_TRIANGLES
    render_triangle([(-0.1, -0.5), (0.1, -0.5), (-0.1, -0.2)], (0.3, 0.3, 0.1))
    render_triangle([(-0.1, -0.2                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      ), (0.1, -0.5), (0.1, -0.2)], (0.3, 0.3, 0.1))


def render_rain():
    glColor3f(0.7, 0.7, 1.0)
    glBegin(GL_POINTS)
    for raindrop in rain_positions:
        glVertex2f(raindrop['x'], raindrop['y'])
    glEnd()


def update_rain_position():
    global rain_positions
    for raindrop in rain_positions:
        raindrop['x'] += rain_dx
        raindrop['y'] -= rain_fall_speed
        if raindrop['y'] < -1.0:  # Reset when off screen
            raindrop['y'] = 1.0
            raindrop['x'] = random.uniform(-1, 1)
    glutPostRedisplay()


def change_background_color():
    global background_color, is_daytime
    if is_daytime:
        background_color = [min(c + 0.01, 0.8) for c in background_color]  # Brighten
    else:
        background_color = [max(c - 0.01, 0.1) for c in background_color]  # Darken


def initialize_window():
    glClear(GL_COLOR_BUFFER_BIT)
    glClearColor(*background_color, 1.0)


def display_func():
    initialize_window()
    render_house()
    render_rain()
    glutSwapBuffers()


def keyboard_func(key, x, y):
    global is_daytime
    if key == b'm':  # Day
        is_daytime = True
        change_background_color()
    elif key == b'n':  # Night
        is_daytime = False
        change_background_color()


def handle_movement(key):
    if key == GLUT_KEY_LEFT:
        return -0.01
    elif key == GLUT_KEY_RIGHT:
        return 0.01


def special_input_func(key, x, y):
    global rain_dx
    rain_dx = handle_movement(key)


def timer_func(value):
    update_rain_position()
    glutTimerFunc(15, timer_func, 0)


# initialization 
glutInit(sys.argv)
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(window_width, window_height)
glutCreateWindow(b"House in Rainfall")
glutDisplayFunc(display_func)
glutKeyboardFunc(keyboard_func)
glutSpecialFunc(special_input_func)
glutTimerFunc(15, timer_func, 0)
glutMainLoop()




# #################################### TASK 2 ###################################
# from OpenGL.GL import *
# from OpenGL.GLUT import *
# from OpenGL.GLU import *
# import random

# # Global variables 
# window_width = 800
# window_height = 600
# particle_list = []  # List of particles (x, y, dx, dy, color, blink_status)
# movement_speed = 0.01  # Initial speed
# is_frozen = False  # freezing movement
# is_blinking = False  # blinking effect

# def create_particle(x, y):
#     dx = random.choice([-1, 1]) * movement_speed
#     dy = random.choice([-1, 1]) * movement_speed
#     color = [random.random() for _ in range(3)]  # Random RGB color
#     particle_list.append({'x': x, 'y': y, 'dx': dx, 'dy': dy, 'color': color, 'blink_status': True})

# def update_particles():
#     if is_frozen:
#         return
#     for particle in particle_list:
#         particle['x'] += particle['dx']
#         particle['y'] += particle['dy']
#         # Bounce off walls
#         if particle['x'] >= 1 or particle['x'] <= -1:
#             particle['dx'] *= -1
#         if particle['y'] >= 1 or particle['y'] <= -1:
#             particle['dy'] *= -1

# def render_particles():
#     for particle in particle_list:
#         if is_blinking and not particle['blink_status']:
#             continue  # Skip drawing
#         glColor3f(*particle['color'])
#         glPointSize(5)
#         glBegin(GL_POINTS)
#         glVertex2f(particle['x'], particle['y'])
#         glEnd()

# def toggle_blink_effect():
#     if is_frozen:
#         return
#     for particle in particle_list:
#         particle['blink_status'] = not particle['blink_status']

# def display_func():
#     glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
#     glLoadIdentity()
#     glViewport(0, 0, window_width, window_height) 
#     glClearColor(0.0, 0.0, 0.0, 1.0) # Black background
#     render_particles()
#     glutSwapBuffers()

# def mouse_func(button, state, x, y):
#     if is_frozen or state != GLUT_DOWN:
#         return
#     # mouse coordinates to OpenGL coordinates
#     openGL_x = (x / window_width) * 2 - 1
#     openGL_y = -((y / window_height) * 2 - 1)
#     if button == GLUT_RIGHT_BUTTON:
#         create_particle(openGL_x, openGL_y)
#     elif button == GLUT_LEFT_BUTTON:
#         global is_blinking
#         is_blinking = not is_blinking

# def keyboard_func(key, x, y):
#     global is_frozen, movement_speed
#     if key == b' ':
#         is_frozen = not is_frozen  # frozen state
#     elif key == b'\x1b':  # Escape key
#         glutLeaveMainLoop()  # Close the window
#         return 

# def special_input_func(key, x, y):
#     global movement_speed
#     if is_frozen:
#         return
#     if key == GLUT_KEY_UP:
#         movement_speed += 0.005  # Increase speed
#     elif key == GLUT_KEY_DOWN:
#         movement_speed = max(0.005, movement_speed - 0.005) 
#     # Update speed 
#     for particle in particle_list:
#         particle['dx'] = (particle['dx'] / abs(particle['dx'])) * movement_speed if particle['dx'] != 0 else movement_speed
#         particle['dy'] = (particle['dy'] / abs(particle['dy'])) * movement_speed if particle['dy'] != 0 else movement_speed

# def timer_func(value):
#     if not is_frozen:
#         update_particles()
#     if is_blinking:
#         toggle_blink_effect()
#     glutPostRedisplay()
#     glutTimerFunc(100 if is_blinking else 15, timer_func, 0)  

# def reshape_func(width, height):
#     global window_width, window_height
#     window_width = width
#     window_height = height
#     glViewport(0, 0, width, height)
#     glMatrixMode(GL_PROJECTION)
#     glLoadIdentity()
#     glOrtho(-1, 1, -1, 1, -1, 1)
#     glMatrixMode(GL_MODELVIEW)

# # initialization
# glutInit()
# glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
# glutInitWindowSize(window_width, window_height)
# glutCreateWindow(b"Random Particles Bouncing and Blinking")
# glutDisplayFunc(display_func)
# glutMouseFunc(mouse_func)
# glutKeyboardFunc(keyboard_func)
# glutSpecialFunc(special_input_func)
# glutReshapeFunc(reshape_func)
# glutTimerFunc(15, timer_func, 0)
# glutMainLoop()


