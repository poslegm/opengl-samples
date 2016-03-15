import glfw
from OpenGL.GL import *
from OpenGL.GLU import *


global direction
global rotate
global speed

def key_callback(window, key, scancode, action, mods):
    global direction
    global rotate
    global speed

    if key == glfw.KEY_LEFT and action == glfw.PRESS:
       direction = 1
    elif key == glfw.KEY_RIGHT and action == glfw.PRESS:
       direction = -1
    elif key == glfw.KEY_ENTER and action == glfw.PRESS:
        rotate = not rotate
    elif key == glfw.KEY_UP and action == glfw.PRESS and speed < 300.0:
        speed += 10.0
        print("Speed: " + str(speed))
    elif key == glfw.KEY_DOWN and action == glfw.PRESS and speed > 10.0:
        speed -= 10.0
        print("Speed: " + str(speed))


def draw_quad():
    glBegin(GL_QUADS)

    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-0.6, 0.6, 0.0)
    glVertex3f(-0.6, -0.6, 0.0)
    glVertex3f(0.6, -0.6, 0.0)
    glVertex3f(0.6, 0.6, 0.0)

    glEnd()


def rotate_figure(window):
    global direction
    global rotate
    global speed

    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    if rotate:
        glRotatef(glfw.get_time() * direction * speed, 0.0, 0.0, 1.0)

    draw_quad()


def main():
    global direction
    global rotate
    global speed
    direction = 1
    rotate = False
    speed = 80.0

    if not glfw.init():
        print("GLFW not initialized")
        return

    window = glfw.create_window(640, 480, "Hello World", None, None)
    if not window:
        print("Window not created")
        glfw.terminate()
        return

    glfw.make_context_current(window)

    glfw.set_key_callback(window, key_callback)

    while not glfw.window_should_close(window):
        rotate_figure(window)

        glfw.swap_buffers(window)

        glfw.poll_events()

    print("Terminate...")
    glfw.terminate()

if __name__ == "__main__":
    main()
