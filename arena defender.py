from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random
# ---------- Window ----------
W, H = 1200, 720
# ---------- Rooms config ----------
rooms = [
    {"name": "Start Room", "size": 60, "wall_height": 25.0, "wall_thick": 0.5, "floor_color": (1, 0.21, 0.88)},
    {"name": "Middle Room", "size": 90, "wall_height": 30.0, "wall_thick": 0.5, "floor_color": (0.5, 0.8, 0.5)},
    {"name": "Final Room", "size": 110, "wall_height": 35.0, "wall_thick": 0.5, "floor_color": (0.537, 0.655, 1)}
]
current_room_index = 0
DOOR_WIDTH = 10
enemy_types = ["rolling_ball", "cube_bot", "spider"]
enemies = []  # list of dicts for each enemy
MAX_ENEMIES_PER_ROOM = 5
game_over = False
levels_completed = 0
has_key = False
key_pos = None 
game_won = False
weapon_pickups = []
# ---------- Camera ----------
camera = {
    "distance": 25.0,   # third person distance
    "height": 15.0,     # above player
    "angle": 180.0,     # horizontal orbit (degrees)
    "pitch": 0.0        # vertical tilt
}
# ---------- Player ----------
player = {
    "x": 0.0,
    "y": 0.0,
    "z": 0.0,
    "speed": 1.0,
    "size": 1.0,
    "angle": 180,
    "health": 100,
    "weapon": None
}
# OpenGL Init 
def init_gl():
    glClearColor(0.05, 0.07, 0.10, 1.0)
def reshape(w, h):
    if h == 0:
        h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, w/float(h), 0.1, 500.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
# Drawing Functions 
def draw_player():
    glPushMatrix()
    glTranslatef(player["x"], 1.0, player["z"])
    glRotatef(player["angle"], 0, 1, 0)
    if game_over:
        glRotatef(90, 1, 0, 0)
        glTranslatef(0, -1.8 * player["size"]/2, 0)
    # Body
    glPushMatrix()
    glScalef(0.90, 1.8, 0.7)
    glTranslatef(0,0.6,0)
    glColor3f(0.2, 0.6, 1.0)
    glutSolidSphere(player["size"], 16, 16)
    glPopMatrix()
    # Head
    glPushMatrix()
    glTranslatef(0.0, 3.1, 0.0)
    glColor3f(1.0, 0.8, 0.6)
    glutSolidSphere(0.6, 16, 16)
    glPopMatrix()
    # Hair
    glPushMatrix()
    glTranslatef(0.0, 3.7, 0)
    glScalef(1.3, 0.4, 0.7)
    glColor3f(0, 0, 0)
    glutSolidCube(1)
    glPopMatrix()
    # Arms
    glPushMatrix()
    glTranslatef(-1.0, 1.2, 0.0)
    glRotatef(90, 0, 0, 1)
    glColor3f(1.0, 0.8, 0.6)
    gluCylinder(gluNewQuadric(),0.2,0.1, 1.2, 8, 8)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(1.0, 1.2, 0.0)
    glRotatef(-90, 0, 0, 1)
    glColor3f(1.0, 0.8, 0.6)
    gluCylinder(gluNewQuadric(),0.2,0.1, 1.2, 8, 8)
    glPopMatrix()
    # Legs
    glPushMatrix()
    glTranslatef(-0.4, -0.2, 0.0)
    glRotatef(90, 1, 0, 0)
    glColor3f(0.3, 0.3, 0.8)
    gluCylinder(gluNewQuadric(), 0.25, 0.15, 1.5, 8, 8)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.4, -0.2, 0.0)
    glRotatef(90, 1, 0, 0)
    glColor3f(0.3, 0.3, 0.8)
    gluCylinder(gluNewQuadric(), 0.25, 0.15, 1.5, 8, 8)
    glPopMatrix()
    glPopMatrix()
def clamp_player():
    margin = 2.0
    room = rooms[current_room_index]
    limit = room["size"] - margin
    # Allow player to move through door on north wall
    if player["z"] >= room["size"] - 5:  # near north wall
        player["x"] = max(-DOOR_WIDTH/2, min(DOOR_WIDTH/2, player["x"]))
        # Allow z to slightly exceed north wall
        player["z"] = min(room["size"] + 5, player["z"])
    else:
        player["x"] = max(-limit, min(limit, player["x"]))
        player["z"] = max(-limit, min(limit, player["z"]))

def draw_floor(size):
    room = rooms[current_room_index]
    base_color = room["floor_color"]
    glPushMatrix()
    max_radius = 2 * size
    step = 6
    for r in range(max_radius, 0, -step):
        color_factor = r / max_radius
        glColor3f(
            base_color[0] * color_factor,
            base_color[1] * color_factor,
            base_color[2] * color_factor
        )
        glPushMatrix()
        glScalef(r, 1, r)
        glutSolidCube(1)
        glPopMatrix()
    glPopMatrix()
def draw_walls():
    room = rooms[current_room_index]
    half = room["size"]
    h = room["wall_height"]
    t = room["wall_thick"]

    # Define gradient colors for walls (bottom, top)
    # bottom_color = (0, 0.078, 0.31)
    bottom_color = (0, 0.0, 0)
    top_color = (0.3, 0.4, 0.8)

    def draw_wall(x, y, z, sx, sy, sz):
        glPushMatrix()
        glTranslatef(x, y , z)
        glScalef(sx, sy, sz)

        glBegin(GL_QUADS)
        # Front face
        glColor3f(*bottom_color)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glColor3f(*top_color)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        # Back face
        glColor3f(*bottom_color)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        glColor3f(*top_color)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        # Left face
        glColor3f(*bottom_color)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        glColor3f(*top_color)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        # Right face
        glColor3f(*bottom_color)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glColor3f(*top_color)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glEnd()

        glPopMatrix()

    # North wall (split for door)
    draw_wall(-half + (half - DOOR_WIDTH)/2, h/2, half, half - DOOR_WIDTH, h, t)
    draw_wall(half - (half - DOOR_WIDTH)/2, h/2, half, half - DOOR_WIDTH, h, t)

    # South wall
    draw_wall(0, h/2, -half, 2*half, h, t)
    # East wall
    draw_wall(half, h/2, 0, t, h, 2*half)
    # West wall
    draw_wall(-half, h/2, 0, t, h, 2*half)

#swap enemies

def spawn_enemies():
    """Spawn random enemies in the current room."""
    global enemies
    # enemies = []
    for e in enemies:
        e["damage_cooldown"] = 0
    room = rooms[current_room_index]
    half = room["size"] - 5  # keep away from walls
    for _ in range(MAX_ENEMIES_PER_ROOM):
        etype = random.choice(enemy_types)
        ex = random.uniform(-half, half)
        ez = random.uniform(-half, half)
        detect = 30 + 5 * current_room_index
        enemies.append({"type": etype,
                        "x": ex,
                        "z": ez,
                        "dir": random.uniform(0, 360),
                        "size": 2.0,
                        "detect_radius": detect,
                        "damage_cooldown": 0,
                        "health": 10
        })
def spawn_key():
    global key_pos
    room = rooms[current_room_index]
    half = room["size"] - 5
    corners = [(-half, -half), (half, -half)]
    key_pos = random.choice(corners)

def spawn_weapon_pickups():
    """Spawn random weapon pickups in the current room."""
    global weapon_pickups
    weapon_pickups = []  # clear old pickups
    room = rooms[current_room_index]
    half = room["size"] - 5

    for i in range(3):  # spawn 3 pickups per room
        wx = random.uniform(-half, half)
        wz = random.uniform(-half, half)
        wtype = i + 1  # weapon type 1, 2, or 3
        weapon_pickups.append({"x": wx, "z": wz, "type": wtype})
def update_enemies():
    global player, game_over, game_won
    room = rooms[current_room_index]
    half = room["size"] - 1
    if game_over or game_won:
        return 
    # damage per room
    damages = [20, 30, 40]
    damage = damages[min(current_room_index, len(damages)-1)]
    base_speed = 0.01
    speed = base_speed + 0.003 * current_room_index

    for e in enemies:
        # distance to player
        dx = player["x"] - e["x"]
        dz = player["z"] - e["z"]
        dist = math.hypot(dx, dz)

        # chase if within detect radius
        if dist < e["detect_radius"]:
            angle = math.atan2(dx, dz)  # angle to player
            e["x"] += math.sin(angle) * speed
            e["z"] += math.cos(angle) * speed
        else:
            # wander
            rad = math.radians(e["dir"])
            e["x"] += math.sin(rad) * base_speed
            e["z"] += math.cos(rad) * base_speed

        # bounce off walls
        if abs(e["x"]) > half or abs(e["z"]) > half:
            e["dir"] = (e["dir"] + 180) % 360

        # collision damage
    # Remove dead enemies
    for e in enemies[:]:  # iterate over a copy
        if e.get("health", 1) <= 0:  # if enemy has 0 or less health
            enemies.remove(e)

    for e in enemies:
        if e["damage_cooldown"] > 0:
            e["damage_cooldown"] -= 1  # one frame per tick

        # collision damage (rate limited)
        dx = player["x"] - e["x"]
        dz = player["z"] - e["z"]
        dist = math.hypot(dx, dz)

        if dist < e["size"]:  
            if e["damage_cooldown"] <= 0:
                player["health"] -= damage  
                e["damage_cooldown"] = 600  
                print("Player health:", player["health"])
                if player["health"] <= 0 and not game_over:
                    print("You Died!")
                    game_over = True


def draw_key(x, z):
    glPushMatrix()
    glTranslatef(x, 1.0, z)
    glColor3f(1.0, 1.0, 0.0)  # yellow
    glutSolidTorus(0.1, 0.4, 8, 16)  # ring
    glTranslatef(0.0, 0.0, 0.3)
    glutSolidCube(0.3)  # key teeth
    glPopMatrix()                


def draw_weapon_pickups():
    for w in weapon_pickups:
        glPushMatrix()
        glTranslatef(w["x"], 1.2, w["z"]) 
        glScalef(2.0, 2.0, 2.0)  

        
        if w["type"] == 1:
            glColor3f(1.0, 1.0, 0.0)  # yellow pistol

            # Body
            glPushMatrix()
            glTranslatef(0.0, 0.05, 0.0)
            glScalef(1.0, 0.25, 0.3)
            glutSolidCube(1)
            glPopMatrix()

            # Barrel
            glPushMatrix()
            glTranslatef(0.6, 0.05, 0.0)
            glScalef(0.6, 0.15, 0.15)
            glutSolidCube(1)
            glPopMatrix()

            # Grip
            glPushMatrix()
            glTranslatef(-0.25, -0.2, 0.0)
            glRotatef(-15, 0, 0, 1)
            glScalef(0.3, 0.5, 0.2)
            glutSolidCube(1)
            glPopMatrix()

        elif w["type"] == 2:
            glColor3f(0.5, 1.0, 1.0)  # cyan RPG
            glPushMatrix()
            glRotatef(-90, 1, 0, 0)
            gluCylinder(gluNewQuadric(), 0.25, 0.25, 1.5, 16, 12)
            glPopMatrix()
        elif w["type"] == 3:
            glColor3f(1.0, 0.6, 0.0)  # orange double-barrel
            # left barrel
            glPushMatrix()
            glTranslatef(-0.15, 0, 0)
            glRotatef(-90, 1, 0, 0)
            gluCylinder(gluNewQuadric(), 0.1, 0.1, 1.0, 12, 8)
            glPopMatrix()
            # right barrel
            glPushMatrix()
            glTranslatef(0.15, 0, 0)
            glRotatef(-90, 1, 0, 0)
            gluCylinder(gluNewQuadric(), 0.1, 0.1, 1.0, 12, 8)
            glPopMatrix()
        glPopMatrix()

def draw_enemies():
    """Draw all enemies in the room."""
    for e in enemies:
        if e["type"] == "rolling_ball":
            draw_rolling_ball(e["x"], e["z"], e["size"])
        elif e["type"] == "cube_bot":
            draw_cube_bot(e["x"], e["z"], e["size"])
        elif e["type"] == "spider":
            draw_spider(e["x"], e["z"], e["size"])
#Enemy Drawing Functions
def draw_rolling_ball(x, z, size):
    glPushMatrix()
    glTranslatef(x, size/2.5, z)
    glColor3f(1.0, 0.0, 0.0)
    glutSolidSphere(size/1.5, 16, 16)
    glPopMatrix()
    #middle sphere
    glPushMatrix()
    glTranslatef(x, size, z)
    glColor3f(1.0, 1.0, 1.0)
    glutSolidCube(2)
    glPopMatrix()
   
    #upper sphere
    glPushMatrix()
    glTranslatef(x, size+2, z)
    glColor3f(1.0, 0.0, 0.0)
    glutSolidSphere(size/2, 16, 16)
    glPopMatrix()
def draw_cube_bot(x, z, size):
    glPushMatrix()
    glTranslatef(x, size/2, z)
    # Body
    glPushMatrix()
    glScalef(size, size*1.5, size)
    glColor3f(0.596, 0.286, 0.949)
    glutSolidCube(1)
    glPopMatrix()
    # Legs
    glPushMatrix()
    glTranslatef(-0.3*size, -size, 0)
    glScalef(0.3*size, size, 0.3*size)
    glutSolidCube(1)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.3*size, -size, 0)
    glScalef(0.3*size, size, 0.3*size)
    glutSolidCube(1)
    glPopMatrix()
   
    # Arms
    glPushMatrix()
    glColor3f(1, 0.325, 0.718)
    glTranslatef(-0.75*size, 0.2*size, 0)
    glScalef(0.2*size, size, 0.2*size)
    glutSolidCube(1)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.75*size, 0.2*size, 0)
    glScalef(0.2*size, size, 0.2*size)
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()
def draw_spider(x, z, size):
    y = 0.5  # fixed height above floor
    glPushMatrix()
    glTranslatef(x, y, z)
    # Body
    # glColor3f(0.349, 0.157, 0.106)
    glColor3f(0,0,0)
    glutSolidSphere(size, 16, 16)
    # Head
    # glColor3f(0.749, 0.561, 0.514)
    glColor3f(0.3,0.3,0.3)
    glPushMatrix()
    glTranslatef(0, 0.6*size, size*0.6)
    glutSolidSphere(size*0.6, 12, 12)
    glPopMatrix()
    #front-left
    glPushMatrix()
    glTranslatef(-size, 0, size*0.5)
    glRotatef(-45, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 0.25, 0.15, 1.5, 8, 8)
    glPopMatrix()
    # Front-right
    glPushMatrix()
    glTranslatef(size, 0, size*0.5)
    glRotatef(45, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 0.25, 0.15, 1.5, 8, 8)
    glPopMatrix()
    # Rear-left leg
    glPushMatrix()
    glTranslatef(-size, 0, -size)
    glRotatef(45, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 0.25, 0.15, 1.5, 8, 8)
    glPopMatrix()
    # Rear-right leg
    glPushMatrix()
    glTranslatef(size+1, 0, -size)
    glRotatef(-45, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 0.25, 0.15, 1.5, 8, 8)
    glPopMatrix()
    glPopMatrix()
def check_door_transition():
    global current_room_index, levels_completed,  game_won
    room = rooms[current_room_index]
    half = room["size"]

    can_exit = has_key or len(enemies) == 0
    if can_exit  and (player["z"] >= half - 1.0) and (-DOOR_WIDTH/2 <= player["x"] <= DOOR_WIDTH/2):
        if current_room_index < len(rooms) - 1:
            current_room_index += 1
            levels_completed +=1
            print("Entered:", rooms[current_room_index]["name"])
            load_room(current_room_index)
        else:
            # Player completed last room
            game_won = True
            print("YOU WIN!")
def load_room(index):
    global has_key, key_pos
    room = rooms[index]
    player["x"] = 0
    player["z"] = 0
    camera["angle"] = random.uniform(90,270)
    player["angle"] = camera["angle"]
    camera["pitch"] = 0
    has_key = False
    spawn_enemies()
    spawn_key()
    spawn_weapon_pickups()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    rad = math.radians(camera["angle"])
    pitch_rad = math.radians(camera["pitch"])
    eye_x = player["x"] - camera["distance"] * math.sin(rad)
    eye_z = player["z"] - camera["distance"] * math.cos(rad)
    eye_y = player["y"] + camera["height"] + camera["distance"] * math.sin(pitch_rad)
    gluLookAt(eye_x, eye_y, eye_z,
              player["x"], 1.2, player["z"],
              0, 1, 0)
    room = rooms[current_room_index]
    draw_floor(room["size"])
    draw_walls()
    draw_player()
    update_enemies()
    draw_enemies()
    if weapon_pickups:
        draw_weapon_pickups()
    if key_pos and not has_key:
        draw_key(key_pos[0], key_pos[1])
    if game_over or game_won:
        draw_text()

    glutSwapBuffers()
def idle():
    glutPostRedisplay()
def keyboard(key, x, y):
    global player, game_over, shooting_mode

    if key == b'r' and (game_over or game_won):  # R key to reset after death
        reset_game()
        glutPostRedisplay()
        return  # don't allow movement until reset

    # Movement only if alive
    if game_over or game_won:
        return

    step = player["speed"]
    rad = math.radians(player["angle"])

    if key == b'w':
        player["x"] += math.sin(rad) * step
        player["z"] += math.cos(rad) * step
    elif key == b's':
        player["x"] -= math.sin(rad) * step
        player["z"] -= math.cos(rad) * step
    elif key == b'd':
        player["x"] -= math.cos(rad) * step
        player["z"] += math.sin(rad) * step
    elif key == b'a':
        player["x"] += math.cos(rad) * step
        player["z"] -= math.sin(rad) * step
    elif key == b' ':
        if player["weapon"] is not None:  # only shoot if weapon picked up
            shooting_mode = player["weapon"]  # ensure correct mode
            shoot()

    clamp_player()
    check_weapon_pickup()
    check_key_pickup()
    check_door_transition()
    glutPostRedisplay()


def reset_game():
    global player, current_room_index, game_over, player_lying, enemies, game_won, has_key, key_pos

    player["x"] = 0
    player["z"] = 0
    player["angle"] = 180
    player["health"] = 100
    player["weapon"] = None
    current_room_index = 0
    game_over = False
    game_won = False
    player_lying = False
    has_key = False
    key_pos = None
    enemies.clear() 
    load_room(0)

def draw_text():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, W, 0, H, -1, 1)  # screen coordinates: (0,0) bottom-left
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Text color
    glColor3f(1.0, 0.0, 0.0)
    if game_over:
        message = f"GAME OVER! You completed {levels_completed} level(s)"
    elif game_won:
        glColor3f(0.0, 1.0, 0.0)
        message = "YOU WIN!"
    else:
        message = ""

    if message:
        x = W // 2
        y = H // 2
        glRasterPos2f(x - (len(message) * 8) // 2, y)
        for ch in message:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def check_key_pickup():
    global has_key, key_pos
    if key_pos and not has_key:
        dx = player["x"] - key_pos[0]
        dz = player["z"] - key_pos[1]
        if dx*dx + dz*dz < 4:  # within 2 units
            has_key = True
            print("Key collected!")
            key_pos = None

def check_weapon_pickup():
    global shooting_mode, weapon_pickups
    for w in weapon_pickups[:]:
        dx = player["x"] - w["x"]
        dz = player["z"] - w["z"]
        if dx*dx + dz*dz < 2.0**2:  # within 2 units
            player["weapon"] = w["type"]
            shooting_mode = w["type"]
            print(f"Picked up weapon {shooting_mode}!")
            weapon_pickups.remove(w)

def special_keys(key, x, y):
    if key == GLUT_KEY_RIGHT:
        camera["angle"] -= 6.0
        player["angle"] = camera["angle"]
    elif key == GLUT_KEY_LEFT:
        camera["angle"] += 6.0
        player["angle"] = camera["angle"]
    elif key == GLUT_KEY_UP:
        camera["pitch"] = min(camera["pitch"] + 2.0, 80.0)
    elif key == GLUT_KEY_DOWN:
        camera["pitch"] = max(camera["pitch"] - 2.0, -10.0)
    glutPostRedisplay()
# --
def main():
    glutInit([])
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(W, H)
    glutInitWindowPosition(100, 80)
    glutCreateWindow(b"3D Multi-Room Arena")
    init_gl()
    glutReshapeFunc(reshape)
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    spawn_enemies()
    load_room(0)
    glutMainLoop()
   
#Shooting System 

import time
# Bullet state
bullets = []  
shooting_mode = 1 
_last_update_time = None
def _enemy_radius(e):
    # simple circular bounds per enemy type
    if e["type"] == "cube_bot":
        return e["size"] * 0.8
    elif e["type"] == "rolling_ball":
        return e["size"]
    else:  # spider
        return e["size"] * 1.0
def shoot():
    """Fire bullets according to current shooting_mode."""
    global bullets
    # spawn from player center, slightly above floor
    y = 1.2
    ang = math.radians(player["angle"])
    px, pz = player["x"], player["z"]
    def add_bullet(direction_angle, speed, radius, ttl, color):
        vx = math.sin(direction_angle)
        vz = math.cos(direction_angle)
        bullets.append({
            "x": px, "y": y, "z": pz,
            "vx": vx, "vz": vz,
            "speed": speed,
            "radius": radius,
            "ttl": ttl,
            "color": color
        })
    if shooting_mode == 1:
        # Fast, small single bullet
        add_bullet(ang, speed=45.0, radius=0.18, ttl=3.0, color=(1.0, 1.0, 0.0))
    elif shooting_mode == 2:
        # Large, slow single bullet
        add_bullet(ang, speed=20.0, radius=0.5, ttl=4.0, color=(0.5, 1.0, 1.0))
    else:
        # Spread: multiple bullets with slight angle offsets
        for off in (-15.0, -7.5, 0.0, 7.5, 15.0):
            add_bullet(ang + math.radians(off), speed=35.0, radius=0.18, ttl=2.5, color=(1.0, 0.6, 0.0))
def _update_bullets(dt):
    """Move bullets, handle lifetime, walls, and collisions."""
    global bullets, enemies
    room = rooms[current_room_index]
    half = room["size"] + 2.0  
    survivors = []
    for b in bullets:
        b["x"] += b["vx"] * b["speed"] * dt
        b["z"] += b["vz"] * b["speed"] * dt
        b["ttl"] -= dt
        
        if b["ttl"] <= 0 or abs(b["x"]) > half or abs(b["z"]) > half:
            continue
        hit_index = None
        for i, e in enumerate(enemies):
            dx = e["x"] - b["x"]
            dz = e["z"] - b["z"]
            if dx*dx + dz*dz <= (b["radius"] + _enemy_radius(e))**2:
                hit_index = i
                break
        if hit_index is not None:
            enemies.pop(hit_index)  
            
            continue
        survivors.append(b)
    bullets = survivors
def _draw_bullets():
    for b in bullets:
        glPushMatrix()
        glTranslatef(b["x"], b["y"], b["z"])
        glColor3f(b["color"][0], b["color"][1], b["color"][2])
        glutSolidSphere(b["radius"], 12, 12)
        glPopMatrix()
def _bullets_tick_and_draw():
    global _last_update_time
    now = time.time()
    dt = 0.0 if _last_update_time is None else now - _last_update_time
    
    if dt > 0.05:
        dt = 0.05
    _last_update_time = now
    _update_bullets(dt)
    _draw_bullets()

_orig_draw_enemies = draw_enemies
def draw_enemies_with_bullets():
    _orig_draw_enemies()       # original enemy rendering
    _bullets_tick_and_draw()   # then bullets (update + render)
draw_enemies = draw_enemies_with_bullets  # rebind name used by display()
_orig_keyboard = keyboard

#enemy health
def _enemy_max_health(etype):
    
    if etype == "spider":
        return 15   
    elif etype == "cube_bot":
        return 9    
    elif etype == "rolling_ball":
        return 6    
    else:
        return 5


_orig_spawn_enemies = spawn_enemies
def spawn_enemies_with_health():
    
    _orig_spawn_enemies()
    
    for e in enemies:
        
        e["max_health"] = _enemy_max_health(e["type"])
        if "health" not in e:
            e["health"] = e["max_health"]
spawn_enemies = spawn_enemies_with_health

_orig_shoot = shoot
def shoot_with_damage():
    
    before = len(bullets)
    _orig_shoot()
    added = bullets[before:]
    # set damage by shooting_mode
    if shooting_mode == 1:
        dmg = 2  # fast small bullets -> medium damage
    elif shooting_mode == 2:
        dmg = 3  # large slow bullet -> max damage
    else:
        dmg = 1  # spread -> least damage per pellet
    for b in added:
        b["damage"] = dmg
# rebind name
shoot = shoot_with_damage

_orig_update_bullets = _update_bullets
def _update_bullets_with_health(dt):
    global bullets, enemies
    room = rooms[current_room_index]
    half = room["size"] + 2.0  # small slack to let them reach the door gap
    survivors = []
    for b in bullets:
        # move
        b["x"] += b["vx"] * b["speed"] * dt
        b["z"] += b["vz"] * b["speed"] * dt
        b["ttl"] -= dt
        # out of time or bounds?
        if b["ttl"] <= 0 or abs(b["x"]) > half or abs(b["z"]) > half:
            continue
        hit_index = None
        for i, e in enumerate(enemies):
            dx = e["x"] - b["x"]
            dz = e["z"] - b["z"]
            if dx*dx + dz*dz <= (b["radius"] + _enemy_radius(e))**2:
                # damage the enemy (use bullet's damage if present)
                dmg = b.get("damage", None)
                if dmg is None:
                    # fallback: try to infer from radius (not necessary but safe)
                    if b["radius"] >= 0.4:
                        dmg = 3
                    elif b["radius"] <= 0.18:
                        # could be spread or fast small - default to medium
                        dmg = 2
                    else:
                        dmg = 1
                # ensure enemy has health
                if "health" not in e:
                    e["health"] = _enemy_max_health(e["type"])
                    e["max_health"] = e["health"]
                e["health"] -= dmg
                # remove enemy only if health <= 0
                if e["health"] <= 0:
                    enemies.pop(i)
                hit_index = i
                break
        if hit_index is not None:
            # bullet consumed after hit
            continue
        survivors.append(b)
    bullets = survivors

_update_bullets = _update_bullets_with_health

# Health bar drawing functions

def draw_health_bar_for_enemy(e):
   
    if "health" not in e or "max_health" not in e:
        return
    max_h = float(e.get("max_health", 1))
    cur_h = float(max(0, e.get("health", 0)))
    if max_h <= 0:
        ratio = 0.0
    else:
        ratio = cur_h / max_h
    # position above enemy
    x = e["x"]
    z = e["z"]
    y = e.get("size", 2.0) + 2.2  # a little above head
    bar_width = 3.0
    bar_height = 0.22
    filled = bar_width * ratio
    # Save GL state
    glPushAttrib(GL_ENABLE_BIT | GL_COLOR_BUFFER_BIT)
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)
    glDepthFunc(GL_LEQUAL)
    glPushMatrix()
    # move to enemy pos
    glTranslatef(x, y, z)
    # rotate to face camera horizontally
    glRotatef(-camera["angle"] + 180.0, 0, 1, 0)
    # background (dark)
    glColor3f(0.08, 0.08, 0.08)
    glBegin(GL_QUADS)
    glVertex3f(-bar_width/2, 0.0, 0.0)
    glVertex3f(bar_width/2, 0.0, 0.0)
    glVertex3f(bar_width/2, bar_height, 0.0)
    glVertex3f(-bar_width/2, bar_height, 0.0)
    glEnd()
    # choose color (green -> yellow -> red)
    if ratio > 0.6:
        col = (0.0, 1.0, 0.0)
    elif ratio > 0.3:
        col = (1.0, 1.0, 0.0)
    else:
        col = (1.0, 0.0, 0.0)
    # filled portion (slightly in front so it doesn't z-fight)
    glColor3f(col[0], col[1], col[2])
    glBegin(GL_QUADS)
    glVertex3f(-bar_width/2, 0.005, 0.001)
    glVertex3f(-bar_width/2 + filled, 0.005, 0.001)
    glVertex3f(-bar_width/2 + filled, bar_height-0.005, 0.001)
    glVertex3f(-bar_width/2, bar_height-0.005, 0.001)
    glEnd()
    glPopMatrix()
    glPopAttrib()
def draw_all_health_bars():
    for e in enemies:
        draw_health_bar_for_enemy(e)

def draw_enemies_with_bullets_and_health():
    # draw original enemies
    _orig_draw_enemies()
    # update & draw bullets (this may damage enemies)
    _bullets_tick_and_draw()
    # draw health bars for remaining enemies
    draw_all_health_bars()
# final rebind used by display()
draw_enemies = draw_enemies_with_bullets_and_health
#scoreboard/hud
hud = {
    "health": player["health"],
    "max_health": 100,
    "score": 0,
    "wave": 1
}

def _hud_text(x, y, s, font=GLUT_BITMAP_HELVETICA_18):
    """Draw bitmap text at (x,y) in current 2D ortho space (pixels)."""
    glRasterPos2f(x, y)
    for ch in s:
        glutBitmapCharacter(font, ord(ch))

def draw_scoreboard_hud():
    """2D overlay: health bar, score, current room/wave."""
    # Save matrices & state
    glPushAttrib(GL_ENABLE_BIT | GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Setup orthographic projection in window pixels
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, W, 0, H)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Panel settings
    pad = 14
    panel_w = 340
    panel_h = 110
    x0 = 12
    y0 = H - panel_h - 12  # top-left corner

    # Panel background
    glColor4f(0.05, 0.05, 0.08, 0.65)
    glBegin(GL_QUADS)
    glVertex2f(x0,         y0)
    glVertex2f(x0+panel_w, y0)
    glVertex2f(x0+panel_w, y0+panel_h)
    glVertex2f(x0,         y0+panel_h)
    glEnd()

    # Border
    glColor4f(1, 1, 1, 0.15)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x0,         y0)
    glVertex2f(x0+panel_w, y0)
    glVertex2f(x0+panel_w, y0+panel_h)
    glVertex2f(x0,         y0+panel_h)
    glEnd()

    # Text lines
    line1_y = y0 + panel_h - pad - 4
    line2_y = line1_y - 28
    line3_y = line2_y - 28

    room_idx = current_room_index + 1
    total_rooms = len(rooms)
    room_name = rooms[current_room_index]["name"]
    wave = hud.get("wave", room_idx)

    # Labels
    glColor3f(0.95, 0.97, 1.0)
    _hud_text(x0 + pad, line1_y, f"Room {room_idx}/{total_rooms}: {room_name}")
    _hud_text(x0 + pad, line2_y, f"Wave: {wave}")
    _hud_text(x0 + pad, line3_y, f"Score: {hud.get('score', 0)}")

    # Health bar
    hp = float(max(player["health"], 0))
    hpmax = float(max(1, hud.get("max_health", 100)))
    ratio = hp / hpmax
    bar_x = x0 + pad
    bar_y = y0 + pad + 8
    bar_w = panel_w - 2*pad
    bar_h = 18

    # background
    glColor3f(0.15, 0.15, 0.20)
    glBegin(GL_QUADS)
    glVertex2f(bar_x,         bar_y)
    glVertex2f(bar_x+bar_w,   bar_y)
    glVertex2f(bar_x+bar_w,   bar_y+bar_h)
    glVertex2f(bar_x,         bar_y+bar_h)
    glEnd()

    # color gradient choice
    if ratio > 0.6:
        col = (0.1, 0.85, 0.25)
    elif ratio > 0.3:
        col = (0.95, 0.85, 0.10)
    else:
        col = (0.95, 0.15, 0.10)

    # fill
    fill_w = bar_w * ratio
    glColor3f(*col)
    glBegin(GL_QUADS)
    glVertex2f(bar_x,         bar_y)
    glVertex2f(bar_x+fill_w,  bar_y)
    glVertex2f(bar_x+fill_w,  bar_y+bar_h)
    glVertex2f(bar_x,         bar_y+bar_h)
    glEnd()

    # health text overlay
    glColor3f(0.98, 0.98, 0.99)
    _hud_text(bar_x + 6, bar_y + 3, f"HP: {int(hp)}/{int(hpmax)}")

    # Restore matrices & state
    glPopMatrix()  # modelview
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopAttrib()

# Hook scoring: add points when enemies die during bullet updates
_prev_update_bullets_for_score = _update_bullets
def _update_bullets_scored(dt):
    before = len(enemies)
    _prev_update_bullets_for_score(dt)
    after = len(enemies)
    kills = max(0, before - after)
    if kills:
        hud["score"] = hud.get("score", 0) + kills * 10  # +10 per kill
_update_bullets = _update_bullets_scored

#Hook room loads to keep wave in sync with room index
_orig_load_room_for_hud = load_room
def load_room_with_wave(index):
    hud["wave"] = index + 1
    _orig_load_room_for_hud(index)
load_room = load_room_with_wave

# Inject HUD drawing right before the buffer swap by wrapping draw_enemies 
_prev_draw_enemies_for_hud = draw_enemies
def draw_enemies_with_hud():
    _prev_draw_enemies_for_hud()  # enemies, bullets, enemy HP bars
    draw_scoreboard_hud()         # finally overlay the HUD
draw_enemies = draw_enemies_with_hud
# END SCOREBOARD / HUD
if __name__ == "__main__":
    main()
