from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(0, 0, 5, 0, 0, 0, 0, 1, 0)  
    glColor3f(1, 1, 1)                    
    glRotatef(30, 1, 1, 0)
    glutWireOctahedron()
    glFlush()

def keyboard(key, x, y):
    if key == b'b':
        print("Coordenadas:", x, y)
    elif key == b'q':
        glutLeaveMainLoop()

def init():
    glEnable(GL_DEPTH_TEST)
    glClearColor(0, 0, 0, 1)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, 1, 1, 50)
    glMatrixMode(GL_MODELVIEW)

glutInit()
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(400, 400)
glutCreateWindow(b"Octaedro 3D - b: coordenadas | q: sair")
init()
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutMainLoop()
