import glfw
import itertools as itertools
from OpenGL.GL import *


def key_callback(window, key, scancode, action, mods):
    global clear, mode
    if key == glfw.KEY_1 and action == glfw.PRESS and mode != 1:
        mode = 1
        clear = True
    elif key == glfw.KEY_1 and action == glfw.PRESS:
        mode = 1
    elif key == glfw.KEY_2 and action == glfw.PRESS:
        mode = 2
    elif key == glfw.KEY_3 and action == glfw.PRESS:
        mode = 3


def mouse_button_callback(window, button, action, mods):
    global x, y, clicked
    if button == glfw.MOUSE_BUTTON_1 and action == glfw.PRESS:
        x, y = glfw.get_cursor_pos(window)
        clicked = True


def resize_callback(window, width, height):
    if width < height:
        glViewport(0, 0, width, width)
    else:
        glViewport(0, 0, height, height)


def merge_dicts(dicts):
    keys = set().union(*dicts)
    dicts = {k: [i.get(k, []) for i in dicts] for k in keys}
    return {k: list(itertools.chain(*v)) for k, v in dicts.items()}


def compute_intersections(x1, y1, x2, y2):
    # используется целочисленный алгоритм Брезенхэма
    if y2 - y1 == 0:
        # случай с горизонтальным ребром не рассматривается
        return {}

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    # определяется направление движения
    y_step = 1 if y1 < y2 else -1
    x_step = 1 if x1 < x2 else -1

    x = x1
    e = 0
    de = dx
    w = dy
    intersections = {}
    for y in range(y1, y2 + y_step, y_step):
        intersections.setdefault(y, []).append(x)
        e += de
        if 2 * e >= w:
            x += x_step
            e -= w
        else:
            e += de

    return intersections


def get_sorted_intersections(vertexes):
    edges = [(vertexes[i], vertexes[i + 1]) for i in range(-1, len(vertexes) - 1)]
    print(edges)
    intersections = [compute_intersections(x1, y1, x2, y2) for (x1, y1), (x2, y2) in edges]
    # предыдущее действие возвращало список словарей, где ключ - y, а значение - x
    # далее происходит слияние этих словарей в один
    intersections = merge_dicts(intersections)

    intersections = {k: sorted(v) for k, v in intersections.items()}

    return intersections


def create_matrix(width, height, intersections, color):
    matrix = [[(0.0, 0.0, 0.0) for _ in range(width)] for _ in range(height)]
    for k, v in intersections.items():
        for i in range(0, len(v) - 1, 2):
            for x in range(v[i], v[i + 1]):
                matrix[k][x] = color
    return matrix


def prepare_projection(width, height):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, width, 0.0, height, 1.0, -1.0)
    glMatrixMode(GL_MODELVIEW)


def draw_points(coordinates, color):
    glPointSize(2.0)
    glBegin(GL_POINTS)
    glColor3f(*color)
    for x, y in coordinates:
        glVertex2f(x, y)
    glEnd()


def draw_lines(coordinates, color):
    if len(coordinates) > 1:
        glBegin(GL_LINE_STRIP)
        glColor3f(*color)
        for x, y in coordinates:
            glVertex2f(x, y)
        glEnd()


# 1. произвольное задание многоугольника и отрисовка через GL_LINE
# 2. заливка многоугольника пикселями
# 3. применение сглаживания
# TODO обработать изменение размера окна
# TODO найти более эффективный способ работы с матрицей пикселей

def main():
    global clear, x, y, clicked, mode
    mode = 1
    clicked = False
    clear = True

    if not glfw.init():
        print("GLFW not initialized")
        return

    window = glfw.create_window(640, 640, "Rasterization", None, None)
    if not window:
        print("Window not created")
        glfw.terminate()
        return

    glfw.make_context_current(window)

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)

    glfw.set_key_callback(window, key_callback)
    glfw.set_framebuffer_size_callback(window, resize_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)

    figure = []
    intersections = None
    color = (1.0, 0.1, 0.0)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        width, height = glfw.get_window_size(window)
        prepare_projection(width, height)

        if clear:
            figure = []
            intersections = None
            matrix = None
            clear = False

        if mode == 1:
            if clicked:
                figure.append((int(x), int(height - y)))
            draw_points(figure, color)
            draw_lines(figure, color)
            clicked = False
        elif mode == 2:
            if intersections is None:
                print(figure)
                intersections = get_sorted_intersections(figure)
                matrix = create_matrix(width, height, intersections, color)
            if matrix is not None:
                glDrawPixels(width, height, GL_RGB, GL_FLOAT, matrix)
        elif mode == 3:
            pass

        glfw.swap_buffers(window)
        glfw.poll_events()

    print("Terminate...")
    glfw.terminate()


if __name__ == "__main__":
    main()
