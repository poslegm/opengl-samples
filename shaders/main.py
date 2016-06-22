import json
import math

import OpenGL.GL as GL
import glfw
import numpy as np
from PIL import Image

from figures import SurfaceOfRevolution


class Globals:
    fill = True
    rotate_x = 0
    rotate_y = 0
    rotate_z = 0
    scale = 1.0
    shift = [0.0, 0.0]
    segments_count = 40
    isometric = False
    to_cylinder = False
    with_texture = True
    tween = 0
    projection_matrix = np.identity(4, np.float32)
    projection_matrix_id = 0
    modification_matrix_id = 0
    surface_color_id = 0
    position_id = 0


def key_callback(window, key, scancode, action, mods):
    drotate = 0.05
    dscale = 0.05
    dshift = 0.03
    dsegments = 1

    if key == glfw.KEY_F and action == glfw.PRESS:
        Globals.fill = not Globals.fill
    elif key == glfw.KEY_UP:
        Globals.rotate_x -= drotate
    elif key == glfw.KEY_DOWN:
        Globals.rotate_x += drotate
    elif key == glfw.KEY_RIGHT:
        Globals.rotate_y += drotate
    elif key == glfw.KEY_LEFT:
        Globals.rotate_y -= drotate
    elif key == glfw.KEY_Z:
        Globals.rotate_z += drotate
    elif key == glfw.KEY_X:
        Globals.rotate_z -= drotate
    elif key == glfw.KEY_I and Globals.scale < 1.9:
        Globals.scale += dscale
    elif key == glfw.KEY_R and Globals.scale > 0.1:
        Globals.scale -= dscale
    elif key == glfw.KEY_W:
        Globals.shift[1] += dshift
    elif key == glfw.KEY_S:
        Globals.shift[1] -= dshift
    elif key == glfw.KEY_D:
        Globals.shift[0] += dshift
    elif key == glfw.KEY_A:
        Globals.shift[0] -= dshift
    elif key == glfw.KEY_L and Globals.segments_count > 5:
        Globals.segments_count -= dsegments
    elif key == glfw.KEY_M and Globals.segments_count < 100:
        Globals.segments_count += dsegments
    elif key == glfw.KEY_P and action == glfw.PRESS:
        Globals.isometric = not Globals.isometric
    elif key == glfw.KEY_ENTER and action == glfw.PRESS:
        Globals.to_cylinder = not Globals.to_cylinder
    elif key == glfw.KEY_1 and action == glfw.PRESS:
        save_data()
    elif key == glfw.KEY_2 and action == glfw.PRESS:
        load_data()


def resize_callback(window, width, height):
    if width < height:
        GL.glViewport(0, 0, width, width)
    else:
        GL.glViewport(0, 0, height, height)


def make_projection(is_isometric):
    a = 0.61
    l = 1
    if is_isometric:
        m1 = [[1, 0, 0, 0],
              [0, 1, 0, 0],
              [0, 0, -1, 0],
              [0, 0, 0, 1]]
        m2 = [[1, 0, -l * math.cos(a), 0],
              [0, 1, -l * math.sin(a), 0],
              [0, 0, 1, 0],
              [0, 0, 0, 1]]
        Globals.projection_matrix = np.matrix(m1).T * np.matrix(m2).T
    else:
        Globals.projection_matrix = np.identity(4, 'float32')


# вычисление координат для квадратичной твининг-анимации
def quadratic_tween(t, q, r, s):
    return ((1 - t) ** 2) * q + (2 * t * (1 - t)) * r + (t ** 2) * s


def transform_coordinates(t, q, r, s):
    if len(q) != len(r) or len(q) != len(s):
        print("Error in transform_coordinates: coordinates tuples' lengths not equal")
        return ()

    return tuple(quadratic_tween(t, q[i], r[i], s[i]) for i in range(len(q)))


# вычисление текущей кривой для твининг-анимации
def transform_line(tween, start_line, middle_line, end_line):
    if len(start_line) != len(middle_line) or len(start_line) != len(end_line):
        print("Error in transform_line: lines' lengths not equal")
        return ()

    return tuple(
        transform_coordinates(tween, start_line[i], middle_line[i], end_line[i])
        for i in range(len(start_line))
    )


def load_image(image_name):
    im = Image.open(image_name)
    try:
        ix, iy, image = im.size[0], im.size[1], im.tobytes("raw", "RGBA", 0, -1)
    except SystemError:
        ix, iy, image = im.size[0], im.size[1], im.tobytes("raw", "RGBX", 0, -1)

    texture_id = GL.glGenTextures(1)

    GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
    GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
    GL.glTexImage2D(
        GL.GL_TEXTURE_2D, 0, 3, ix, iy, 0,
        GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, image
    )

    return texture_id


def create_shader(shader_type, source):
    shader = GL.glCreateShader(shader_type)

    GL.glShaderSource(shader, source)
    GL.glCompileShader(shader)

    status = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
    if not status:
        log = GL.glGetShaderInfoLog(shader)
        print(log)

    return shader


def load_shaders():
    program = GL.glCreateProgram()

    vertex = create_shader(GL.GL_VERTEX_SHADER, """
    #version 130

    attribute vec3 position;

    uniform mat4 projection_matrix;
    uniform mat4 modification_matrix;

    void main(){
        gl_Position = projection_matrix * modification_matrix * vec4(position, 1.0);
    }""")

    fragment = create_shader(GL.GL_FRAGMENT_SHADER, """
    #version 130

    uniform vec4 surface_color;

    out vec4 outputColour;
    void main() {
        outputColour = surface_color;
    }""")

    GL.glAttachShader(program, vertex)
    GL.glAttachShader(program, fragment)
    GL.glLinkProgram(program)
    status = GL.glGetProgramiv(program, GL.GL_LINK_STATUS)
    if not status:
        log = GL.glGetProgramInfoLog(program)
        print(log)

    Globals.position_id = GL.glGetAttribLocation(program, "position")
    Globals.projection_matrix_id = GL.glGetUniformLocation(program, "projection_matrix")
    Globals.modification_matrix_id = GL.glGetUniformLocation(program, "modification_matrix")
    Globals.surface_color_id = GL.glGetUniformLocation(program, "surface_color")

    return program


def draw_shader(program, color, mod_matrix):
    GL.glUseProgram(program)
    GL.glUniform4f(Globals.surface_color_id, *color)
    GL.glUniformMatrix4fv(Globals.projection_matrix_id, 1, GL.GL_FALSE, Globals.projection_matrix.tolist())
    GL.glUniformMatrix4fv(Globals.modification_matrix_id, 1, GL.GL_FALSE, mod_matrix.tolist())


def init():
    if not glfw.init():
        print("GLFW not initialized")
        return

    window = glfw.create_window(640, 640, "Cubes", None, None)
    if not window:
        print("Window not created")
        glfw.terminate()
        return

    glfw.make_context_current(window)

    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glDepthFunc(GL.GL_LESS)

    glfw.set_key_callback(window, key_callback)
    glfw.set_framebuffer_size_callback(window, resize_callback)

    # подключение шейдеров
    program = load_shaders()

    return window, program


def save_data():
    file = open("dump", 'w')
    keys = (
        "fill", "rotate_x", "rotate_y", "rotate_z", "scale", "_Globals__current_ambient_color_index",
        "shift", "segments_count", "isometric", "light_model_local_viewer", "light_model_two_side",
        "to_cylinder", "texture", "tween"
    )
    globals_dict = {key: Globals.__dict__[key] for key in keys}
    file.write(json.dumps(globals_dict))
    file.close()
    print("Данные сохранены")


def load_data():
    try:
        file = open("dump", 'r')
        parameters = json.loads(file.read())
        Globals.fill = parameters["fill"]
        Globals.rotate_x = parameters["rotate_x"]
        Globals.rotate_y = parameters["rotate_y"]
        Globals.rotate_z = parameters["rotate_z"]
        Globals.scale = parameters["scale"]
        Globals.shift = parameters["shift"]
        Globals.segments_count = parameters["segments_count"]
        Globals.isometric = parameters["isometric"]
        Globals.to_cylinder = parameters["to_cylinder"]
        Globals.tween = parameters["tween"]
    except IOError:
        print("Ошибка при чтении файла")


line = (
    (0.0, 0.65, 0.0),
    (0.2, 0.4, 0.0),
    (0.05, 0.4, 0.0),
    (0.35, 0.0, 0.0),
    (0.08, 0.0, 0.0),
    (0.08, -0.15, 0.0),
    (0.0, -0.15, 0.0)
)
middle_line = (
    (0.0, 0.65, 0.0),
    (0.2, 0.525, 0.0),
    (0.125, 0.525, 0.0),
    (0.275, 0.0, 0.0),
    (0.14, 0.0, 0.0),
    (0.14, -0.15, 0.0),
    (0.0, -0.15, 0.0)
)
end_line = (
    (0.0, 0.65, 0.0),
    (0.2, 0.65, 0.0),
    (0.2, 0.65, 0.0),
    (0.2, 0.0, 0.0),
    (0.2, 0.0, 0.0),
    (0.2, -0.15, 0.0),
    (0.0, -0.15, 0.0)
)


def main():
    surface_color = (0.0, 0.6, 0.1, 1.0)
    window, shader_program = init()
    surface = SurfaceOfRevolution(line, [0.0, 0.0, 0.0], Globals.position_id)

    deltat = 0.02
    current_line = line

    while not glfw.window_should_close(window):
        # изменение параметра для анимации
        if Globals.to_cylinder and Globals.tween < 1:
            Globals.tween += deltat
            current_line = transform_line(Globals.tween, line, middle_line, end_line)
        elif not Globals.to_cylinder and Globals.tween > 0:
            Globals.tween -= deltat
            current_line = transform_line(Globals.tween, line, middle_line, end_line)

        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        make_projection(Globals.isometric)

        surface.change_line(current_line)
        surface.change_segments_count(Globals.segments_count)
        mod_matrix = surface.draw(
            Globals.shift, Globals.fill, Globals.scale,
            Globals.rotate_x, Globals.rotate_y, Globals.rotate_z
        )

        draw_shader(shader_program, surface_color, mod_matrix)

        # после каждой итерации сдвиг снова становится нулевым до тех пор,
        # пока пользователь не нажмёт кнопку
        Globals.shift = [0.0, 0.0]

        glfw.swap_buffers(window)
        glfw.poll_events()

    print("Terminate...")
    glfw.terminate()


if __name__ == "__main__":
    main()
