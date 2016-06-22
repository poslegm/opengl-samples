import OpenGL.GL as GL
import math
import numpy as np
import ctypes


class SurfaceOfRevolution:
    @staticmethod
    def __get_delta(segments_count, i, r):
        angle = 2.0 * math.pi * i / segments_count
        dx = r * math.cos(angle)
        dz = r * math.sin(angle)
        return dx, dz

    def __compute_grid(self, segments_count):
        self.__grid = []

        i = 0
        while i < len(self.__vertices) - 1:
            v1 = self.__vertices[i]
            v2 = self.__vertices[i + 1]

            r1 = math.sqrt(v1[0] ** 2 + v1[2] ** 2)
            r2 = math.sqrt(v2[0] ** 2 + v2[2] ** 2)

            for j in range(segments_count):
                dx1, dz1 = self.__get_delta(segments_count, j, r1)
                dx2, dz2 = self.__get_delta(segments_count, j, r2)

                self.__grid.append([(dx1, v1[1], dz1), (dx2, v2[1], dz2)])

                dx1, dz1 = self.__get_delta(segments_count, j + 1, r1)
                dx2, dz2 = self.__get_delta(segments_count, j + 1, r2)

                self.__grid[-1].append((dx2, v2[1], dz2))
                self.__grid[-1].append((dx1, v1[1], dz1))

            i += 1

    # вычисление нормалей нужно для освещения
    # нормали хранятся в виде одномерного списка координат
    def __compute_normals(self):
        self.__normals = []
        for polygon in self.__grid:
            p1, p2, p3, _ = polygon
            self.__normals.extend(self.__create_normal(p1, p2, p3) * 4)

    @staticmethod
    def __create_normal(a, b, c):
        v1 = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
        v2 = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
        return [
            v1[1] * v2[2] - v1[2] * v2[1],
            v1[2] * v2[0] - v1[0] * v2[2],
            v1[0] * v2[1] - v1[1] * v2[0]
        ]

    def __create_vao(self):
        grid_array = np.array(self.__grid, dtype=np.float32).flatten()
        textures_array = np.array(self.__texture_coordinates * len(self.__grid), dtype=np.float32).flatten()

        vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(vao)

        vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)

        GL.glEnableVertexAttribArray(self.__position_id)
        GL.glVertexAttribPointer(self.__position_id, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, ctypes.c_void_p(0))
        # сразу после координат вершин в буфере будут лежать координаты текстуры
        # поэтому указатель смещается на sizeof(float) * длину массива координат вершин
        # GL.glVertexAttribPointer(
        #     self.__texture_id, 2, GL.GL_FLOAT,
        #     GL.GL_FALSE, 0, ctypes.c_void_p(4 * len(grid_array))
        # )

        GL.glBufferData(
            GL.GL_ARRAY_BUFFER, grid_array.nbytes,
            grid_array, GL.GL_STATIC_DRAW
        )

        # GL.glBufferData(
        #     GL.GL_ARRAY_BUFFER, grid_array.nbytes + textures_array.nbytes,
        #     np.concatenate((grid_array, textures_array)), GL.GL_STATIC_DRAW
        # )
        GL.glBindVertexArray(0)

        GL.glDisableVertexAttribArray(self.__position_id)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

        self.__vao = vao

    def __compute_all(self):
        self.__compute_grid(self.__segments_count)
        self.__compute_normals()
        self.__create_vao()

    def __init__(self, vertices, center, position_id, texture_id, segments_count=40):
        self.__vao = None
        self.__center = center
        self.__vertices = vertices
        self.__segments_count = segments_count
        self.__position_id = position_id
        self.__texture_id = texture_id
        self.__compute_all()

    def change_line(self, vertices):
        if vertices != self.__vertices:
            self.__vertices = vertices
            self.__compute_all()

    def change_segments_count(self, segments_count):
        if segments_count != self.__segments_count:
            self.__segments_count = segments_count
            self.__compute_all()

    __texture_coordinates = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))

    @staticmethod
    def __translate(center):
        return np.matrix(
            [[1, 0, 0, 0],
             [0, 1, 0, 0],
             [0, 0, 1, 0],
             [center[0], center[1], center[2], 1]]
        )

    @staticmethod
    def __scale(scale):
        return np.matrix(
            [[scale, 0, 0, 0],
             [0, scale, 0, 0],
             [0, 0, scale, 0],
             [0, 0, 0, 1]]
        )

    @staticmethod
    def __rotate(angle_x, angle_y, angle_z):
        sx, sy, sz = math.sin(angle_x), math.sin(angle_y), math.sin(angle_z)
        cx, cy, cz = math.cos(angle_x), math.cos(angle_y), math.cos(angle_z)
        rot_x = np.matrix(
            [[1, 0, 0, 0],
             [0, cx, sx, 0],
             [0, -sx, cx, 0],
             [0, 0, 0, 1]]
        )
        rot_y = np.matrix(
            [[cy, 0, -sy, 0],
             [0, 1, 0, 0],
             [sy, 0, cy, 0],
             [0, 0, 0, 1]]
        )
        rot_z = np.matrix(
            [[cz, sz, 0, 0],
             [-sz, cz, 0, 0],
             [0, 0, 1, 0],
             [0, 0, 0, 1]]
        )
        return rot_x * rot_y * rot_z

    def draw(
            self, shift, fill, scale=1.0, angle_x=0, angle_y=0, angle_z=0,
            with_texture=False, with_lightning=False
    ):
        self.__center[0] += shift[0]
        self.__center[1] += shift[1]

        mod_matrix = self.__translate(self.__center) \
                     * self.__scale(scale) \
                     * self.__rotate(angle_x, angle_y, angle_z)

        if fill:
            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        else:
            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)

        if with_texture:
            GL.glEnable(GL.GL_TEXTURE_2D)
        else:
            GL.glDisable(GL.GL_TEXTURE_2D)

        # if with_lightning:
        #     GL.glNormalPointer(GL.GL_FLOAT, 0, self.__normals)
        GL.glBindVertexArray(self.__vao)
        GL.glDrawArrays(GL.GL_QUADS, 0, len(self.__grid) * 4)
        GL.glBindVertexArray(0)

        return mod_matrix
