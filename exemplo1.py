from OpenGL.GL import *
from OpenGL.GLUT import *

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    
    glBegin(GL_POLYGON)
    glVertex3f(0.25, 0.25, 0.00)
    glVertex3f(0.75, 0.25, 0.00)
    glVertex3f(0.75, 0.75, 0.00)
    glVertex3f(0.25, 0.75, 0.00)
    glEnd()

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE|GLUT_RGB)
    glutInitWindowSize(250,250)
    glutInitWindowPosition(100,100)
    glutCreateWindow(b"Hello Word!")
    init()
    glutDisplayFunc(display)
    glutMainLoop()

def init():
    glClearColor(0.0, 0.0,0.0,1.0)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.1,1.0,0.0,1.0,-1.0,1.0)
    glMatrixMode(GL_MODELVIEW)
if __name__ == "__main__":
    main()