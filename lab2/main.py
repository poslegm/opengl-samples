import glfw
import math
from OpenGL.GL import *


class Cube:
    __sides = ((0, 1, 2, 3), (3, 2, 7, 6), (6, 7, 5, 4),
               (4, 5, 1, 0), (1, 5, 7, 2), (4, 0, 3, 6))

    __colors = ((0, 0, 1, 1), (0, 1, 1, 1), (1, 1, 1, 1),
                (1, 1, 0, 1), (1, 0, 0, 1), (1, 0, 1, 1))

    def __init__(self, center, size):
        self.__center = center
        coord = size / 2
        self.__vertices = (
            (coord, -coord, -coord), (coord, coord, -coord),
            (-coord, coord, -coord), (-coord, -coord, -coord),
            (coord, -coord, coord), (coord, coord, coord),
            (-coord, -coord, coord), (-coord, coord, coord)
        )

    def draw(self, fill, scale=1.0, angle_x=0, angle_y=0):
        glLoadIdentity()
        glPushMatrix()

        glTranslatef(*self.__center)
        glScalef(scale, scale, scale)
        glRotatef(angle_x, 1, 0, 0)
        glRotatef(angle_y, 0, 1, 0)

        if fill:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        glBegin(GL_QUADS)
        for i in range(len(self.__sides)):
            if fill:
                glColor4f(*self.__colors[i])
            for vertex in self.__sides[i]:
                glVertex3f(*self.__vertices[vertex])
        glEnd()

        glPopMatrix()


def key_callback(window, key, scancode, action, mods):
    global fill
    global rotate_x
    global rotate_y
    global scale
    if key == glfw.KEY_F and action == glfw.PRESS:
        fill = not fill
    elif key == glfw.KEY_UP:
        rotate_x -= 5
    elif key == glfw.KEY_DOWN:
        rotate_x += 5
    elif key == glfw.KEY_RIGHT:
        rotate_y += 5
    elif key == glfw.KEY_LEFT:
        rotate_y -= 5
    elif key == glfw.KEY_W and scale < 1.9:
        scale += 0.05
    elif key == glfw.KEY_S and scale > 0.1:
        scale -= 0.05


def resize_callback(window, width, height):
    if width < height:
        glViewport(0, 0, width, width)
    else:
        glViewport(0, 0, height, height)


def main():
    global fill
    global rotate_x
    global rotate_y
    global scale
    fill = True
    rotate_x = 0
    rotate_y = 0
    scale = 1.0

    if not glfw.init():
        print("GLFW not initialized")
        return

    window = glfw.create_window(640, 640, "Cubes", None, None)
    if not window:
        print("Window not created")
        glfw.terminate()
        return

    glfw.make_context_current(window)

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)

    glfw.set_key_callback(window, key_callback)
    glfw.set_framebuffer_size_callback(window, resize_callback)

    big_cube = Cube((0.0, 0.0, 0.0), 0.6)
    small_cube = Cube((0.8, 0.8, 0.0), 0.1)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        a = 0.61
        l = 1
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMultTransposeMatrixf([1, 0, 0, 0,
                                0, 1, 0, 0,
                                0, 0, -1, 0,
                                0, 0, 0, 1])
        glMultTransposeMatrixf([1, 0, -l * math.cos(a), 0,
                                0, 1, -l * math.sin(a), 0,
                                0, 0, 1, 0,
                                0, 0, 0, 1])
        glMatrixMode(GL_MODELVIEW)

        big_cube.draw(fill, scale, rotate_x, rotate_y)

        small_cube.draw(fill)

        glfw.swap_buffers(window)
        glfw.poll_events()

    print("Terminate...")
    glfw.terminate()


if __name__ == "__main__":
    main()
