import OpenGL.GL as GL
import glfw


class Globals:
    clip_polygon_vertexes = []
    segments_vertexes = []
    mode = 1
    complete = False
    clipped_segments = []
    clipped_color = (1.0, 1.0, 1.0)
    default_color = (1.0, 0.0, 0.0)

    @staticmethod
    def clear_all():
        Globals.clip_polygon_vertexes.clear()
        Globals.segments_vertexes.clear()
        Globals.clipped_segments.clear()
        Globals.complete = False


def key_callback(window, key, scancode, action, mods):
    if key == glfw.KEY_1 and action == glfw.PRESS and Globals.mode != 1:
        Globals.mode = 1
        Globals.clear_all()
    elif key == glfw.KEY_2 and action == glfw.PRESS:
        Globals.mode = 2
        Globals.complete = True
    elif key == glfw.KEY_3 and action == glfw.PRESS:
        Globals.mode = 3
        Globals.clipped_segments = compute_clipping(Globals.segments_vertexes, Globals.clip_polygon_vertexes)
    elif key == glfw.KEY_ENTER and action == glfw.PRESS:
        Globals.complete = True


def mouse_button_callback(window, button, action, mods):
    x, y = glfw.get_cursor_pos(window)
    _, height = glfw.get_window_size(window)
    y = height - y

    if button == glfw.MOUSE_BUTTON_1 and action == glfw.PRESS and Globals.mode == 1:
        Globals.clip_polygon_vertexes.append((x, y))
    elif button == glfw.MOUSE_BUTTON_1 and action == glfw.PRESS and Globals.mode == 2:
        Globals.segments_vertexes.append((x, y))


def resize_callback(window, width, height):
    GL.glViewport(0, 0, width, height)
    Globals.clear_all()


def prepare_projection(width, height):
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()
    GL.glOrtho(0.0, width, 0.0, height, 1.0, -1.0)
    GL.glMatrixMode(GL.GL_MODELVIEW)


def draw_points(coordinates, color):
    GL.glPointSize(2.0)
    GL.glBegin(GL.GL_POINTS)
    GL.glColor3f(*color)
    for x, y in coordinates:
        GL.glVertex2f(x, y)
    GL.glEnd()


def draw_lines(coordinates, color, is_complete):
    if len(coordinates) > 1:
        if is_complete:
            GL.glBegin(GL.GL_LINE_LOOP)
        else:
            GL.glBegin(GL.GL_LINE_STRIP)
        GL.glColor3f(*color)
        for x, y in coordinates:
            GL.glVertex2f(x, y)
        GL.glEnd()


def draw_segment(start, end, color):
    x1, y1 = start
    x2, y2 = end
    GL.glBegin(GL.GL_LINES)
    GL.glColor3f(*color)
    GL.glVertex2f(x1, y1)
    GL.glVertex2f(x2, y2)
    GL.glEnd()


def draw_segments(coordinates, color):
    if len(coordinates) > 0 and len(coordinates) % 2 != 0:
        draw_points([coordinates[-1]], color)
        vertexes = coordinates[:-1]
    else:
        vertexes = coordinates

    for i in range(0, len(vertexes), 2):
        draw_segment(vertexes[i], vertexes[i + 1], color)


def create_edges(vertexes):
    return [(vertexes[i], vertexes[i + 1]) for i in range(-1, len(vertexes) - 1)]


def create_segments(vertexes):
    if len(vertexes) % 2 != 0:
        vs = vertexes[:-1]
    else:
        vs = vertexes

    return [(vs[i], vs[i + 1]) for i in range(0, len(vs), 2)]


def create_vector(start, end):
    x1, y1 = start
    x2, y2 = end
    return x2 - x1, y2 - y1


def dot_product(v1, v2):
    x1, y1 = v1
    x2, y2 = v2
    return x1 * x2 + y1 * y2


# косое произведение векторов v1v2 и v1v3
def skew_product(v1, v2, v3):
    x1, y1 = v1
    x2, y2 = v2
    x3, y3 = v3
    return (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)


# поиск пересечений алгоритмом параметрического отсечения с упорядочиванием точек пересечения
def find_intersections(edges, segment):
    ts = []

    for edge in edges:
        x1, y1 = v0 = edge[0]
        x2, y2 = v1 = edge[1]

        normal = (y2 - y1, x1 - x2)

        p0, p1 = segment[0], segment[1]

        # если косые произведения векторов от обоих концов отрезка и ребра имеет одинаковый
        # знак, то обе вершины лежат по одну сторону от ребра => пересечений с ним нет
        if skew_product(p0, p1, v0) * skew_product(p0, p1, v1) > 0:
            continue

        n = dot_product(create_vector(v0, p0), normal)
        d = dot_product(create_vector(p0, p1), normal)

        # если d == 0, то они параллельны
        if d == 0:
            continue

        t = - n / d

        print((edge, p(p0, p1, t), d < 0))

        ts.append(t)

    ts = sorted(ts)
    print("ts:")
    print(ts)

    return ts


# пересечение двух числовых отрезков, представленных как кортежи
def get_overlap(i1, i2):
    if i1[1] < i2[0] or i2[1] < i1[0]:
        return None
    else:
        return max(i1[0], i2[0]), min(i1[1], i2[1])


def compute_clipping(segments_vertexes, figure_vertexes):
    segments = create_segments(segments_vertexes)
    edges = create_edges(figure_vertexes)
    to_draw = []
    for s in segments:
        intersections = find_intersections(edges, s)
        intersections = [0] + intersections + [1]
        intersections = [(intersections[j], intersections[j + 1]) for j in range(0, len(intersections) - 1, 2)]
        print("Before overlapping: ")
        print(intersections)
        intersections = [get_overlap(t, (0, 1)) for t in intersections if get_overlap(t, (0, 1)) is not None]
        print("After overlapping: ")
        print(intersections)
        intersections = [(p(s[0], s[1], t1), p(s[0], s[1], t2)) for t1, t2 in intersections]
        print("To draw: ")
        print(intersections)
        to_draw += intersections
    return to_draw


# p = p1 + (p1 - p1) * t
def p(p1, p2, t):
    x1, y1, = p1
    x2, y2 = tuple(map(lambda x: x * t, create_vector(p1, p2)))
    return x1 + x2, y1 + y2


def main():
    if not glfw.init():
        print("GLFW not initialized")
        return

    window = glfw.create_window(640, 640, "Clipping", None, None)
    if not window:
        print("Window not created")
        glfw.terminate()
        return

    glfw.make_context_current(window)

    glfw.set_key_callback(window, key_callback)
    glfw.set_framebuffer_size_callback(window, resize_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)

    while not glfw.window_should_close(window):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        width, height = glfw.get_window_size(window)
        prepare_projection(width, height)

        # создание отсекающего многоугольника
        if Globals.mode == 1:
            draw_points(Globals.clip_polygon_vertexes, Globals.default_color)
            draw_lines(Globals.clip_polygon_vertexes, Globals.default_color, Globals.complete)
        # рисование отрезков
        elif Globals.mode == 2:
            draw_lines(Globals.clip_polygon_vertexes, Globals.default_color, Globals.complete)
            draw_segments(Globals.segments_vertexes, Globals.default_color)
        elif Globals.mode == 3:
            draw_lines(Globals.clip_polygon_vertexes, Globals.default_color, Globals.complete)
            draw_segments(Globals.segments_vertexes, Globals.default_color)
            for s in Globals.clipped_segments:
                draw_segment(s[0], s[1], Globals.clipped_color)

        glfw.swap_buffers(window)
        glfw.poll_events()

    print("Terminate...")
    glfw.terminate()


if __name__ == "__main__":
    main()
