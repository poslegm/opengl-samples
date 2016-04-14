import glfw
import itertools as itertools
from OpenGL.GL import *


def key_callback(window, key, scancode, action, mods):
    global clear
    if key == glfw.KEY_C and action == glfw.PRESS:
        clear = True
    elif key == glfw.KEY_D and action == glfw.PRESS:
        clear = False


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
    if y2 - y1 == 0:
        # случай с горизонтальным ребром не рассматривается
        return {}

    dx = abs(x2 - x1) / abs(y2 - y1)
    # определяется направление движения
    y_step = 1 if y1 < y2 else -1
    dx *= 1 if x1 < x2 else -1

    x = x1
    intersections = {}
    for y in range(y1, y2, y_step):
        intersections.setdefault(y, []).append(round(x))
        x += dx
    return intersections


def get_sorted_intersections(vertexes):
    edges = [(vertexes[i], vertexes[i + 1]) for i in range(-1, len(vertexes) - 1)]

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


def main():
    global clear
    clear = False

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

    figure = [
        (0, 0), (0, 100), (100, 100), (150, 50), (100, 0), (50, 50)
    ]
    figure = list(map(lambda coords: (coords[0] * 2, coords[1] * 2), figure))
    scene_width = 300
    scene_height = 300

    intersections = get_sorted_intersections(figure)
    print(intersections)
    matrix = create_matrix(scene_width, scene_height, intersections, (1.0, 0.1, 0.1))

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if not clear:
            glDrawPixels(scene_width, scene_height, GL_RGB, GL_FLOAT, matrix)

        glfw.swap_buffers(window)
        glfw.poll_events()

    print("Terminate...")
    glfw.terminate()


if __name__ == "__main__":
    main()
