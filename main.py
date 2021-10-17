import math
import random
import numpy as np
from PIL import Image
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

EDGES = 12

SCREEN_FRAMES = 60
SCREEN_HEIGHT = 800
SCREEN_WIDTH = 800

g = 9.81

planets_names = ["mercury", "venus", "earth", "mars", "jupiter", "saturn", "uranus", "neptune"]

planets_distances = [14, 25, 32, 40, 70, 105, 130, 160]

planets_radii = [0.4, 0.95, 1, 0.53, 5, 4.5, 2.8, 2.7]

planet_rotations = [math.radians(random.randint(0, 360)) for i in range(8)]

planet_rotations_around_axis = [math.radians(random.randint(0, 360)) for i in range(8)]

planet_rotation_multipliers = [3, 2, 15, 16, 22, 21, 18, 17]

planets_ecliptics = [0.5, 177.4, 23.45, 25.19, 3.12, 26.73, 97.86, 29.56]

sun_rotation = 0

moon_rotation = 0
moon_rotation_around_axis = 0

rotation_lock = False
axis_rotation_lock = False
orbit_draw_flag = False

textures = {}

def load_texture(file):
    img = Image.open(file)
    img_data = np.array(list(img.getdata()), np.int8)
    textID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, textID)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    #glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    return textID

def draw():
    glClearColor(0, 0, 0, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glPushAttrib(GL_LIGHTING_BIT)
    glMaterialfv(GL_FRONT, GL_EMISSION, (1.0, 0.9, 0.9, 0))

    draw_sphere("sun", 10, sun_rotation)
    draw_sphere("stars", 500)
    glPopAttrib()
    #glMaterialfv(GL_FRONT, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    for dist, rot, name, radius, ax_rot, ecl in zip(planets_distances, planet_rotations, planets_names, planets_radii, planet_rotations_around_axis, planets_ecliptics):
        glPushMatrix()
        glTranslatef(math.cos(rot)*dist,0,math.sin(rot)*dist)
        if name == "mercury":
            glTranslatef(0, math.cos(rot)*2.5, 0)
        if name == "earth":
            glPushMatrix()
            glTranslatef(math.cos(moon_rotation)*3.5,0,math.sin(moon_rotation)*3.5)
            draw_sphere("moon", 0.25, -moon_rotation_around_axis)
            glPopMatrix()
        if name == "saturn":
            draw_rings(9, 11, 40, "saturn_rings", ecl)
        draw_sphere(name, radius, ax_rot, ecl)
        glPopMatrix()

    if orbit_draw_flag:
        draw_orbits(100)

    glFlush()
    glutSwapBuffers()

def draw_orbits(points):
    glLineWidth(0.5)
    glPushAttrib(GL_LIGHTING_BIT)
    glMaterialfv(GL_FRONT, GL_EMISSION, (1.0, 0.9, 0.9, 0))
    for dist in planets_distances:
        inclination = 0
        glBegin(GL_LINE_STRIP)
        for p in range(points+1):
            angle = p / float(points) * math.pi * 2.0
            if dist == 14:
                inclination = math.cos(angle)*2.5
            glVertex3f(math.cos(angle)*dist, inclination, math.sin(angle)*dist)
        glEnd()
    glPopAttrib()

def draw_sphere(texture, radius, rot=None, ecliptic=None):
    glPushMatrix()
    glBindTexture(GL_TEXTURE_2D, textures[texture])
    glEnable(GL_TEXTURE_2D)
    quadric = gluNewQuadric()
    gluQuadricDrawStyle(quadric, GLU_FILL)
    gluQuadricTexture(quadric, True)
    gluQuadricNormals(quadric, GLU_SMOOTH)
    glRotatef(90,-1,0,0)
    if ecliptic:
        glRotatef(ecliptic, 0, 1, 0)
    if rot:
        glRotatef(rot, 0, 0, 1)
    glScaled(1, 1, -1)
    gluSphere(quadric,radius,25,25)
    glPopMatrix()

def draw_rings(inner_radius, outer_radius, points, texture, ecl = None):

    vertices = []
    for i in range(points + 1):
        angle = i / float(points) * math.pi * 2.0
        vertices.append(((inner_radius * math.cos(angle), 0, inner_radius * math.sin(angle)), (outer_radius * math.cos(angle), 0, outer_radius * math.sin(angle))))

    glPushAttrib(GL_LIGHTING_BIT)
    glMaterialfv(GL_FRONT, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glBindTexture(GL_TEXTURE_2D, textures[texture])
    glEnable(GL_TEXTURE_2D)
    glPushMatrix()
    glRotatef(90, 0, 1, 0)
    glRotatef(ecl, 1, 0, 0)
    for i in range(1,len(vertices)):
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex3fv(vertices[i-1][0])
        glTexCoord2f(1, 0)
        glVertex3fv(vertices[i-1][1])
        glTexCoord2f(1, 1)
        glVertex3fv(vertices[i][1])
        glTexCoord2f(0, 1)
        glVertex3fv(vertices[i][0])
        glEnd()
    glPopAttrib()
    glPopMatrix()

def keyboard(key, x, y):
    ch = key.decode("utf-8")
    if ch in ['1', '2', '3']:
        if ch == '1':
            global rotation_lock
            rotation_lock = not rotation_lock
        elif ch == '2':
            global axis_rotation_lock
            axis_rotation_lock = not axis_rotation_lock
        elif ch == '3':
            global orbit_draw_flag
            orbit_draw_flag = not orbit_draw_flag
    if ch not in ['w', 'a', 's', 'd', 'z', 'x', 'q', 'e', 'r', 'f', 'c', 'v']:
        return

    glMatrixMode(GL_PROJECTION)
    if ch == 'w':
        glTranslatef(0,0,1)
    elif ch == 's':
        glTranslatef(0,0,-1)
    elif ch == 'a':
        glTranslatef(-1,0,0)
    elif ch == 'd':
        glTranslatef(1,0,0)
    elif ch == 'r':
        glTranslatef(0,1,0)
    elif ch == 'f':
        glTranslatef(0,-1,0)
    elif ch == 'z':
        glRotatef(5, 0, 1, 0)
    elif ch == 'x':
        glRotatef(-5, 0, 1, 0)
    elif ch == 'q':
        glRotatef(-5, 0, 0, 1)
    elif ch == 'e':
        glRotatef(5, 0, 0, 1)
    elif ch == 'c':
        glRotatef(-5, 1, 0, 0)
    elif ch == 'v':
        glRotatef(5, 1, 0, 0)
    glMatrixMode(GL_MODELVIEW)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(SCREEN_WIDTH, SCREEN_HEIGHT)
    glutCreateWindow('Solar system')
    textures["sun"] = load_texture("sun.jpg")
    textures["mercury"] = load_texture("mercury.jpg")
    textures["venus"] = load_texture("venus.jpg")
    textures["earth"] = load_texture("earth.jpg")
    textures["mars"] = load_texture("mars.jpg")
    textures["jupiter"] = load_texture("jupiter.jpg")
    textures["saturn"] = load_texture("saturn.jpg")
    textures["saturn_rings"] = load_texture("saturn_rings.jpg")
    textures["uranus"] = load_texture("uranus.jpg")
    textures["neptune"] = load_texture("neptune.jpg")
    textures["stars"] = load_texture("stars.jpg")
    textures["moon"] = load_texture("moon.jpg")
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_POINT_SMOOTH)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(60, SCREEN_WIDTH/SCREEN_HEIGHT, 1, 1000)
    glTranslatef(0,0,-40) #front
    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (0, 0, 0, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0, 0, 0, 1))

    glutKeyboardFunc(keyboard)
    glutDisplayFunc(draw)
    glutTimerFunc(16, timer, 1)
    glutMainLoop()

def timer(value):
    global planet_rotations
    global sun_rotation
    global moon_rotation
    global moon_rotation_around_axis
    for i in range(len(planet_rotations)):
        if not rotation_lock:
            planet_rotations[i]+=math.radians((1/(planets_distances[i]**2))*100)
        if not axis_rotation_lock:
            planet_rotations_around_axis[i]+=math.radians(planet_rotation_multipliers[i])
    if not axis_rotation_lock:
        sun_rotation += math.radians(2)
        moon_rotation_around_axis += math.radians(45)
    if not rotation_lock:
        moon_rotation += math.radians(1)
    glutTimerFunc(16, timer, 1)
    glutPostRedisplay()

if __name__ == '__main__':
    main()