import glfw
import itertools as itertools
from OpenGL.GL import *
import numpy as np


def key_callback(window, key, scancode, action, mods):
    global clear_all, clear_buffers, mode, complete
    if key == glfw.KEY_1 and action == glfw.PRESS and mode != 1:
        mode = 1
        clear_all = True
    elif key == glfw.KEY_1 and action == glfw.PRESS:
        mode = 1
    elif key == glfw.KEY_2 and action == glfw.PRESS:
        mode = 2
        clear_buffers = True
    elif key == glfw.KEY_3 and action == glfw.PRESS:
        mode = 3
        clear_buffers = True
    elif key == glfw.KEY_C and action == glfw.PRESS:
        clear_all = True
    elif key == glfw.KEY_ENTER and action == glfw.PRESS:
        complete = True


def mouse_button_callback(window, button, action, mods):
    global x, y, clicked
    if button == glfw.MOUSE_BUTTON_1 and action == glfw.PRESS:
        x, y = glfw.get_cursor_pos(window)
        clicked = True


def resize_callback(window, width, height):
    global clear_all, window_height
    window_height = height
    glViewport(0, 0, width, height)
    clear_all = True


def is_doubling_need(x, y, edges):
    edges_with_vertex = list(filter(lambda e: (x, y) in e, edges))
    if len(edges_with_vertex) != 2:
        return True
    # находим вершины, соседние от данной в списке рёбер
    _, y1 = list(filter(lambda e: e[0] != x or e[1] != y, edges_with_vertex[0]))[0]
    _, y2 = list(filter(lambda e: e[0] != x or e[1] != y, edges_with_vertex[1]))[0]
    # дублировать нужно, если вершина не лежит между соседними
    return (y1 > y and y2 > y) or (y1 < y and y2 < y)


def merge_dicts(dicts, edges):
    keys = set().union(*dicts)
    dicts = {k: [i.get(k, []) for i in dicts] for k in keys}
    dicts = {k: sorted(list(itertools.chain(*v))) for k, v in dicts.items()}
    # устранения дублирующихся значений х там, где это не нужно
    for y, xs in dicts.items():
        new_xs = []
        for x in xs:
            x_count = len(list(filter(lambda i: i == x, xs)))
            if x_count > 1 and ((x not in new_xs) or (x in new_xs and is_doubling_need(x, y, edges))):
                new_xs.append(x)
            elif x_count == 1:
                new_xs.append(x)
        dicts[y] = new_xs
    return dicts


def compute_intersections(x1, y1, x2, y2):
    global window_height

    if y1 == y2:
        return {}

    intersections = {}
    for y in range(window_height):
        x = (y - y1) * (x2 - x1) / (y2 - y1) + x1
        if (min(y1, y2) <= y <= max(y1, y2)) and (min(x1, x2) <= x <= max(x1, x2)):
            intersections.setdefault(y, []).append(round(x))
    return intersections


def compute_pixels_smoothing(x1, y1, x2, y2, color, matrix):
    if y2 - y1 == 0:
        # случай с горизонтальным ребром не рассматривается
        return {}

    # используется целочисленный алгоритм Брезенхэма
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    slope = dy > dx

    if slope:
        dx, dy = dy, dx

    if slope and ((x2 < x1 and y2 > y1) or (x1 < x2 and y2 < y1)):
        y2, y1 = y1, y2
        x1, x2 = x2, x1
    elif not slope and ((y1 < y2 and x1 < x2) or (y2 < y1 and x2 < x1)):
        y2, y1 = y1, y2
        x1, x2 = x2, x1

    # определяется направление движения
    y_step = 1 if y1 < y2 else -1
    x_step = 1 if x1 < x2 else -1

    y = y1
    x = x1

    bright_max = 8  # максимальный коэффициент яркости умножается на 10, чтобы арифметика с ним была целочисленной
    bright_min = 0.2
    # все константы домножены на 2 * dx
    e = bright_max * dx
    m = 2 * dy * bright_max
    w = 2 * e
    e_max = w - m

    matrix[y][x] = tuple(map(lambda x: x * (bright_min + bright_max / 20), color))
    for i in range(dx):
        if e >= e_max:
            if slope:
                x += x_step
            else:
                y += y_step
            e -= w
        if slope:
            y += y_step
        else:
            x += x_step
        e += m
        bright = bright_min + e / (2 * dx * 10)
        matrix[y][x] = tuple(map(lambda x: x * bright, color))

    return matrix


def create_edges(vertexes):
    return [(vertexes[i], vertexes[i + 1]) for i in range(-1, len(vertexes) - 1)]


def get_sorted_intersections(vertexes):
    edges = create_edges(vertexes)
    print(edges)
    intersections = [compute_intersections(x1, y1, x2, y2) for (x1, y1), (x2, y2) in edges]
    # предыдущее действие возвращало список словарей, где ключ - y, а значение - x
    # далее происходит слияние этих словарей в один
    intersections = merge_dicts(intersections, edges)
    intersections = {k: sorted(intersections[k]) for k in sorted(intersections.keys())}

    return intersections


def create_matrix(width, height, intersections, color):
    matrix = np.zeros((width, height), dtype='3float32')
    for y, xs in intersections.items():
        for i in range(0, len(xs) - 1, 2):
            for x in range(xs[i], xs[i + 1] + 1):
                matrix[y][x] = color
    return matrix


def add_lines_to_matrix(vertexes, color, matrix):
    edges = create_edges(vertexes)
    for (x1, y1), (x2, y2) in edges:
        compute_pixels_smoothing(x1, y1, x2, y2, color, matrix)
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


def draw_lines(coordinates, color, is_complete):
    if len(coordinates) > 1:
        if is_complete:
            glBegin(GL_LINE_LOOP)
        else:
            glBegin(GL_LINE_STRIP)
        glColor3f(*color)
        for x, y in coordinates:
            glVertex2f(x, y)
        glEnd()


def create_figure_view(width, height, figure, color):
    intersections = get_sorted_intersections(figure)
    matrix = create_matrix(width, height, intersections, color)

    return matrix


# 1. произвольное задание многоугольника и отрисовка через GL_LINE
# 2. заливка многоугольника пикселями
# 3. применение сглаживания

def main():
    global clear_all, clear_buffers, x, y, clicked, mode, complete, window_height
    mode = 1
    clicked, complete = False, False
    clear_all, clear_buffers = True, True
    window_height = 640

    if not glfw.init():
        print("GLFW not initialized")
        return

    window = glfw.create_window(640, window_height, "Rasterization", None, None)
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
    color = (1.0, 1.0, 1.0)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        width, height = glfw.get_window_size(window)
        prepare_projection(width, height)

        if clear_buffers:
            matrix = None
            clear_buffers = False

        if clear_all:
            figure = []
            matrix = None
            clear_all, complete = False, False

        if mode == 1:
            if clicked:
                figure.append((int(x), int(height - y)))
            draw_points(figure, color)
            draw_lines(figure, color, complete)
            clicked = False
        elif mode == 2:
            if matrix is None:
                matrix = create_figure_view(width, height, figure, color)
            glDrawPixels(width, height, GL_RGB, GL_FLOAT, matrix)
        elif mode == 3:
            # фильтрация работает только при задании вершин против часовой стрелки!
            # отрисовка сглаженных границ
            if matrix is None:
                matrix = create_figure_view(width, height, figure, color)
                matrix = add_lines_to_matrix(figure, color, matrix)
            glDrawPixels(width, height, GL_RGB, GL_FLOAT, matrix)

        glfw.swap_buffers(window)
        glfw.poll_events()

    print("Terminate...")
    glfw.terminate()


if __name__ == "__main__":
    main()
