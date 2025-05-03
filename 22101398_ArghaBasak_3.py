from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math

player_coords = [0, 0]
player_angle = 90
player_lives = 5
missed_targets = 0
game_score = 0
game_over = False

window_width, window_height = 1200, 900  
grid_limit = 800  

camera_follow = False
camera_y_offset = 500
camera_x_angle = 0
view_angle = 120

cheat_mode_active = False
cheat_mode_counter = 0
vision_mode_active = False

bullets = []
enemies = []


class Bullet:
    def __init__(self, pos_x, pos_y, direction):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.pos_z = 120                #Bullet Position
        self.direction = direction

    def move(self):
        self.pos_x += 10 * math.cos(math.radians(self.direction - 90))
        self.pos_y += 10 * math.sin(math.radians(self.direction - 90))  # Bullet speed

class Enemy:
    def __init__(self):
        self.reset()

    def reset(self):
        angle = random.uniform(0, 2 * math.pi)
        radius = 500  
        self.pos_x = radius * math.cos(angle)
        self.pos_y = radius * math.sin(angle)
        self.pos_z = 50
        self.base_size = 60  
        self.top_size = 40   
        self.growing = True  

    def approach_player(self):
        dx = player_coords[0] - self.pos_x
        dy = player_coords[1] - self.pos_y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 1:
            self.pos_x += dx / distance * 1.5   #Converting unit vector
            self.pos_y += dy / distance * 1.5

        if self.growing:
            self.base_size += 0.5 
            self.top_size += 0.3   
            if self.base_size >= 70:  
                self.growing = False
        else:
            self.base_size -= 0.5  
            self.top_size -= 0.3   
            if self.base_size <= 50: 
                self.growing = True

        self.base_size = max(50, min(self.base_size, 70))
        self.top_size = max(30, min(self.top_size, 50))

    def draw(self):
    
        glPushMatrix()
        glTranslatef(self.pos_x, self.pos_y, self.pos_z)
        glColor3f(0.9, 0.1, 0.1)
        glutSolidSphere(self.base_size, 20, 20) 
        glPopMatrix()

        glPushMatrix()
        glTranslatef(self.pos_x, self.pos_y, self.pos_z + self.base_size)  
        glColor3f(0.1, 0.1, 0.1)
        glutSolidSphere(self.top_size, 20, 20)  
        glPopMatrix()

def display_text(x, y, message):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for char in message:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_player():
    glPushMatrix()
    glTranslatef(player_coords[0], player_coords[1], 0)
    glRotatef(player_angle, 0, 0, 1)
    glRotatef(90, 1, 0, 0)
    glTranslatef(0, 0, 40)  

    glColor3f(0.2, 0.2, 0.2)
    glTranslatef(0, 250, 0)  
    gluSphere(gluNewQuadric(), 40, 20, 20)  

    glTranslatef(0, -100, 0)
    glPushMatrix()
    glScalef(1.2, 1.4, 0.6)  
    glColor3f(0.1, 0.5, 0.8)
    glutSolidCube(80)  
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-20, -120, 0)
    glRotatef(-90, 1, 0, 0)
    glColor3f(0.7, 0.3, 0.7)
    gluCylinder(gluNewQuadric(), 20, 10, 120, 20, 20)  
    glPopMatrix()

    glPushMatrix()
    glTranslatef(20, -120, 0)
    glRotatef(-90, 1, 0, 0)
    glColor3f(0.7, 0.3, 0.7)
    gluCylinder(gluNewQuadric(), 20, 10, 120, 20, 20)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-60, 15, 3)
    glRotatef(-90, 0, 0, 1)
    glColor3f(0.2, 0.8, 0.2)
    gluCylinder(gluNewQuadric(), 16, 8, 70, 20, 20) 
    glPopMatrix()

    glPushMatrix()
    glTranslatef(60, 15, 3)
    glRotatef(90, 0, 0, 1)
    glColor3f(0.2, 0.8, 0.2)
    gluCylinder(gluNewQuadric(), 16, 8, 70, 20, 20) 
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 15, 3)
    glColor3f(0.9, 0.1, 0.1)
    gluCylinder(gluNewQuadric(), 24, 12, 80, 20, 20)  
    glPopMatrix()

    glPopMatrix()

def draw_bullet(bullet):
    glPushMatrix()
    glTranslatef(bullet.pos_x, bullet.pos_y, bullet.pos_z)
    glColor3f(1, 0, 0)
    glutSolidCube(5)
    glPopMatrix()

def draw_grid():
    square_size = 50  
    for x in range(-grid_limit, grid_limit, square_size):
        for y in range(-grid_limit, grid_limit, square_size):
            glColor3f(0.8, 0.8, 1.0) if (x // square_size + y // square_size) % 2 == 0 else glColor3f(1.0, 1.0, 1.0)
            glBegin(GL_QUADS)
            glVertex3f(x, y, 0)
            glVertex3f(x + square_size, y, 0)
            glVertex3f(x + square_size, y + square_size, 0)
            glVertex3f(x, y + square_size, 0)
            glEnd()

def draw_boundary_walls():
    wall_height = 100
    wall_thickness = 20

    glPushMatrix()
    glColor3f(0.0, 0.0, 1.0)  
    glTranslatef(-grid_limit - wall_thickness / 2, 0, wall_height / 2) #Shifts the Position
    glScalef(wall_thickness, grid_limit * 2, wall_height) #Resize drawing
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.0, 1.0, 0.0)  
    glTranslatef(grid_limit + wall_thickness / 2, 0, wall_height / 2)
    glScalef(wall_thickness, grid_limit * 2, wall_height)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.0, 1.0, 1.0)  
    glTranslatef(0, grid_limit + wall_thickness / 2, wall_height / 2)
    glScalef(grid_limit * 2, wall_thickness, wall_height)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glColor3f(1.0, 0.0, 0.0) 
    glTranslatef(0, -grid_limit - wall_thickness / 2, wall_height / 2)
    glScalef(grid_limit * 2, wall_thickness, wall_height)
    glutSolidCube(1)
    glPopMatrix()

def render_game():
    global bullets, enemies, player_lives, missed_targets, game_score, game_over, cheat_mode_active

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity() #Reset Previous Information
    glViewport(0, 0, window_width, window_height)

    setup_camera()

    if game_over:
        cheat_mode_active = False 
        draw_grid()
        draw_boundary_walls()
        glPushMatrix()
        glTranslatef(player_coords[0], player_coords[1], 0)
        glRotatef(player_angle, 0, 0, 1)
        glRotatef(90, 1, 0, 0)  
        glRotatef(45, 0, 1, 0)  
        draw_player()
        glPopMatrix()
        display_text(40, window_height - 100, f"Life: {player_lives}  Score: {game_score}  Missed: {missed_targets}")
        display_text(40, 700, "GAME OVER! Press 'R' to Restart")
        glutSwapBuffers()
        return

    draw_grid()
    draw_boundary_walls()
    draw_player()

    new_bullets = []
    for bullet in bullets:
        bullet.move()
        if abs(bullet.pos_x) > grid_limit or abs(bullet.pos_y) > grid_limit:
            missed_targets += 1
            continue  
        hit = False
        for enemy in enemies:
            dx = enemy.pos_x - bullet.pos_x
            dy = enemy.pos_y - bullet.pos_y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < enemy.base_size:  
                game_score += 1
                enemy.reset()
                hit = True
                break
        if not hit:
            new_bullets.append(bullet)
        draw_bullet(bullet)

    bullets = new_bullets

    for enemy in enemies:
        enemy.approach_player() 
        enemy.draw()             

    for enemy in enemies:
        dx = enemy.pos_x - player_coords[0]
        dy = enemy.pos_y - player_coords[1]
        if math.sqrt(dx ** 2 + dy ** 2) < enemy.base_size + 30:
            player_lives -= 1
            enemy.reset()

    if player_lives <= 0 or missed_targets >= 10:
        game_over = True

    display_text(40, window_height - 90, f"Life: {player_lives}  Score: {game_score}  Missed: {missed_targets}")
    glutSwapBuffers()

def handle_keyboard(key, x, y):
    global player_coords, player_angle, cheat_mode_active, vision_mode_active, player_lives, game_score, missed_targets, bullets, game_over
    if game_over and key == b'r':
        player_lives = 5
        missed_targets = 0
        game_score = 0
        bullets.clear()
        for enemy in enemies:
            enemy.reset()
        game_over = False
        return

    if game_over:
        return

    if key == b'w':
        player_coords[0] += 20 * math.cos(math.radians(player_angle - 90))
        player_coords[1] += 20 * math.sin(math.radians(player_angle - 90))
    elif key == b's':
        player_coords[0] -= 20 * math.cos(math.radians(player_angle - 90))
        player_coords[1] -= 20 * math.sin(math.radians(player_angle - 90))
    elif key == b'a':
        player_angle += 10
    elif key == b'd':
        player_angle -= 10
    elif key == b'c':  
        cheat_mode_active = not cheat_mode_active
    elif key == b'v':
        vision_mode_active = not vision_mode_active

def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if camera_follow:
        gluPerspective(90, window_width / window_height, 1, 3000)
        offset_x = player_coords[0] + 100 * math.cos(math.radians(player_angle - 90))   # Camera position
        offset_y = player_coords[1] + 100 * math.sin(math.radians(player_angle - 90))
        offset_z = 100
        gluLookAt(offset_x, offset_y, offset_z, 
                  player_coords[0] + 200 * math.cos(math.radians(player_angle - 90)),   # Object Position
                  player_coords[1] + 200 * math.sin(math.radians(player_angle - 90)), 
                  offset_z, 0, 0, 1)
    else:
        gluPerspective(view_angle, window_width / window_height, 1, 2000)
        offset_x = camera_y_offset * math.cos(math.radians(camera_x_angle))
        offset_y = camera_y_offset * math.sin(math.radians(camera_x_angle))
        gluLookAt(offset_x, offset_y, 500, 0, 0, 0, 0, 0, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def handle_special_keys(key, x, y):
    global camera_y_offset, camera_x_angle
    if key == GLUT_KEY_UP:
        camera_y_offset += 20
    elif key == GLUT_KEY_DOWN:
        camera_y_offset -= 20
    elif key == GLUT_KEY_LEFT:
        camera_x_angle -= 5
    elif key == GLUT_KEY_RIGHT:
        camera_x_angle += 5

def handle_mouse(button, state, x, y):
    global camera_follow
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        spawn_x = player_coords[0] + 10 * math.cos(math.radians(player_angle - 90))  #10 = kotoduk dure bullet jawa shuru korbe
        spawn_y = player_coords[1] + 10 * math.sin(math.radians(player_angle - 90))
        spawn_z = 80
        bullets.append(Bullet(spawn_x, spawn_y, player_angle))
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        camera_follow = not camera_follow

def fire_bullets_in_cheat_mode():
    global cheat_mode_counter
    if cheat_mode_counter % 500 == 0:
        for i in range(5):
            bullet_x = player_coords[0] + 10 * math.cos(math.radians(player_angle))
            bullet_y = player_coords[1] + 10 * math.sin(math.radians(player_angle))
            bullets.append(Bullet(bullet_x, bullet_y, player_angle + i * 15 - 30))
    cheat_mode_counter += 1

def idle_update():
    global player_angle
    if cheat_mode_active:
        player_angle += 5
        fire_bullets_in_cheat_mode()
    glutPostRedisplay()

def initialize():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutCreateWindow(b"Bullet Frenzy")
    glEnable(GL_DEPTH_TEST)

    glutDisplayFunc(render_game)
    glutKeyboardFunc(handle_keyboard)
    glutSpecialFunc(handle_special_keys)
    glutMouseFunc(handle_mouse)
    glutIdleFunc(idle_update)

    for _ in range(5):
        enemies.append(Enemy())

    glutMainLoop()

if __name__ == '__main__':
    initialize()
