from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys, math
import time

# --- estado da garra / câmera ---
angulo_braco = 0
angulo_garra = 30

distance = 22.0
azimuth = 40.0
incidence = 25.0
twist = 0.0

target_distance = distance
target_azimuth = azimuth
target_incidence = incidence
target_twist = twist

mouse_last_x = 0
mouse_last_y = 0
mouse_left = False
mouse_right = False

pan_x = 0
pan_y = 0
pan_target_x = 0
pan_target_y = 0

projecao_ortografica = False
rotacao_grade = 0

# novo: modo automático (animação)
auto_mode = False
auto_start = time.time()

# objeto da cena (caixa/crate)
crate_pos = (8.0, 0.0, 6.0)
crate_size = 1.5

def suavizar(valor, alvo, fator=0.15):
    return valor + (alvo - valor) * fator

def desenhaCeu():
    # gradiente de céu suave
    glDisable(GL_LIGHTING)
    glBegin(GL_QUADS)
    glColor3f(0.05, 0.12, 0.30)   # horizonte azul escuro
    glVertex3f(-200, -10, -200)
    glVertex3f(200, -10, -200)

    glColor3f(0.45, 0.75, 0.95)   # parte de cima mais clara
    glVertex3f(200, 120, -400)
    glVertex3f(-200, 120, -400)
    glEnd()
    glEnable(GL_LIGHTING)

def desenhaChao():
    glPushMatrix()
    glRotatef(rotacao_grade, 1, 0, 0)

    # desenha um chão quadriculado (checkered)
    tamanho = 40
    passo = 1
    glNormal3f(0, 1, 0)
    for x in range(-tamanho, tamanho, passo):
        for z in range(-tamanho, tamanho, passo):
            # alterna cor
            if ((x + z) % 2) == 0:
                glColor3f(0.85, 0.85, 0.85)
            else:
                glColor3f(0.65, 0.65, 0.65)
            glBegin(GL_QUADS)
            glVertex3f(x, 0, z)
            glVertex3f(x + passo, 0, z)
            glVertex3f(x + passo, 0, z + passo)
            glVertex3f(x, 0, z + passo)
            glEnd()

    # linha de referência (eixo)
    glBegin(GL_LINES)
    glColor3f(0.8, 0.2, 0.2)
    glVertex3f(0, 0.01, 0)
    glVertex3f(3, 0.01, 0)
    glEnd()

    glPopMatrix()

def caixa(dx, dy, dz, r, g, b):
    glPushMatrix()
    glColor3f(r, g, b)
    glTranslatef(dx/2, dy/2, dz/2)
    glScalef(dx, dy, dz)
    glutSolidCube(1)
    glPopMatrix()

def desenhaCrate():
    x, y, z = crate_pos
    s = crate_size
    glPushMatrix()
    glTranslatef(x, y, z)
    # madeira: tom marrom e um leve brilho
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [0.55, 0.36, 0.20, 1.0])
    # usar caixas compostas para parecer um caixote
    caixa(s, s, s, 0.65, 0.40, 0.20)
    # reset material
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    glPopMatrix()

def desenhaGarra():
    global angulo_garra

    glPushMatrix()

    # base da garra
    caixa(2, 0.4, 1, 0.8, 0.3, 0.3)

    # dedo esquerdo
    glPushMatrix()
    glTranslatef(2, 0, 0)
    glRotatef(angulo_garra, 0, 0, 1)
    caixa(2, 0.4, 1, 0.3, 0.9, 0.9)
    glPopMatrix()

    # dedo direito
    glPushMatrix()
    glTranslatef(2, 0, 0)
    glRotatef(-angulo_garra, 0, 0, 1)
    caixa(2, 0.4, 1, 0.9, 0.3, 0.9)
    glPopMatrix()

    glPopMatrix()

def desenhaBraco():
    glPushMatrix()

    # base do braço
    glPushMatrix()
    glColor3f(0.35, 0.35, 0.45)
    glTranslatef(0, 0.5, 0)
    glScalef(1.2, 1.0, 1.2)
    glutSolidCube(1)
    glPopMatrix()

    # articulação e braço
    glTranslatef(0.5, 0, 0)
    glRotatef(angulo_braco, 0, 1, 0)

    caixa(3, 0.3, 0.3, 0.8, 0.8, 0.8)

    glTranslatef(3, 0, 0)
    desenhaGarra()

    glPopMatrix()

def aplicarCamera():
    global distance, azimuth, incidence, twist
    global pan_x, pan_y

    distance = suavizar(distance, target_distance)
    azimuth = suavizar(azimuth, target_azimuth)
    incidence = suavizar(incidence, target_incidence)
    twist = suavizar(twist, target_twist)
    pan_x = suavizar(pan_x, pan_target_x)
    pan_y = suavizar(pan_y, pan_target_y)

    az = math.radians(azimuth)
    inc = math.radians(incidence)

    eye_x = distance * math.cos(inc) * math.sin(az) + pan_x
    eye_y = distance * math.sin(inc) + pan_y
    eye_z = distance * math.cos(inc) * math.cos(az)

    glRotatef(twist, 0, 0, 1)

    gluLookAt(
        eye_x, eye_y, eye_z,
        pan_x, pan_y, 0,
        0, 1, 0
    )

def escreverTexto(x, y, texto):
    glDisable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 800, 0, 600)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1, 1, 1)
    glRasterPos2f(x, y)
    for c in texto:
        glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord(c)) # type: ignore

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_LIGHTING)

def display():
    global angulo_braco, angulo_garra, auto_mode, auto_start

    # animação automática (se ativa)
    if auto_mode:
        t = time.time() - auto_start
        # braço oscila entre -25 e +25
        angulo_braco = 25.0 * math.sin(t * 0.8)
        # garra abre/fecha entre 10 e 55
        angulo_garra = 32.5 + 22.5 * math.sin(t * 2.2)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    aplicarCamera()

    desenhaCeu()
    desenhaChao()
    desenhaCrate()
    desenhaBraco()

    # HUD
    escreverTexto(10, 570, f"distance = {distance:.1f}   azimuth = {azimuth:.1f}   incidence = {incidence:.1f}   twist = {twist:.1f}")
    escreverTexto(10, 540, "Controles: a/s - abrir/fechar garra | j/l - girar braço | g - toggle auto | p - trocar projecao | ESC - sair")
    escreverTexto(10, 520, "Mouse: arrastar esquerdo = rotacionar | shift + arrastar esquerdo = twist | direito + shift = pan | roda = zoom")

    # indicativo de auto-mode
    if auto_mode:
        escreverTexto(10, 500, "AUTO: ON")
    else:
        escreverTexto(10, 500, "AUTO: OFF")

    glutSwapBuffers()
    glutPostRedisplay()

def keyboard(key, x, y):
    global angulo_garra, angulo_braco, projecao_ortografica, rotacao_grade
    global auto_mode, auto_start

    if key == b'a':
        angulo_garra = min(60, angulo_garra + 2)
    elif key == b's':
        angulo_garra = max(0, angulo_garra - 2)
    elif key == b'j':
        angulo_braco += 5
    elif key == b'l':
        angulo_braco -= 5
    elif key == b'p':
        projecao_ortografica = not projecao_ortografica
        aplicarProjecao()
    elif key == b'x':
        rotacao_grade += 5
    elif key == b'g':
        # toggla modo automático
        auto_mode = not auto_mode
        if auto_mode:
            auto_start = time.time()
    elif key == b'\x1b':
        sys.exit(0)

def aplicarProjecao():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # janela quadrada 800x600 -> aspect = 800/600
    if projecao_ortografica:
        glOrtho(-20, 20, -15, 15, 1, 200)
    else:
        gluPerspective(60, 800/600, 1, 200)
    glMatrixMode(GL_MODELVIEW)

def mouse(button, state, x, y):
    global mouse_left, mouse_right, mouse_last_x, mouse_last_y

    mouse_left = (button == GLUT_LEFT_BUTTON and state == GLUT_DOWN)
    mouse_right = (button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN)

    mouse_last_x = x
    mouse_last_y = y

def motion(x, y):
    global mouse_last_x, mouse_last_y
    global target_azimuth, target_incidence
    global target_twist, pan_target_x, pan_target_y

    dx = x - mouse_last_x
    dy = y - mouse_last_y

    mods = glutGetModifiers()

    if mouse_left:
        if mods == GLUT_ACTIVE_SHIFT:
            target_twist += dx * 0.3
        else:
            target_azimuth += dx * 0.4
            target_incidence -= dy * 0.4

    if mouse_right:
        # com shift faz pan fino
        if mods == GLUT_ACTIVE_SHIFT:
            pan_target_x += dx * 0.05
            pan_target_y += dy * 0.05
        else:
            pan_target_x += dx * 0.1
            pan_target_y += dy * 0.1

    mouse_last_x = x
    mouse_last_y = y

def mouseWheel(button, dir, x, y):
    global target_distance
    # dir: +1 ou -1 dependendo do glut
    target_distance -= dir * 1.5
    target_distance = max(5, min(120, target_distance))

def init():
    glClearColor(0.36, 0.64, 0.90, 1)
    aplicarProjecao()

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)

    # mais iluminação: ambiente + direcional
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, [10.0, 40.0, 20.0, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.6, 0.6, 0.6, 1.0])

    # luz ambiente suave
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.25, 0.25, 0.28, 1.0])

    # materiais com brilho moderado
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.2, 0.2, 0.2, 1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 20.0)

# inicialização GLUT
glutInit(sys.argv)
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(800, 600)
glutCreateWindow(b"Garra - Cena: deposito leve")

init()
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutMouseFunc(mouse)
glutMotionFunc(motion)
glutMouseWheelFunc(mouseWheel)

glutMainLoop()
