from OpenGL.GL import *
import math


class Cube:
    __sides = ((0, 1, 2, 3), (3, 2, 7, 6), (6, 7, 5, 4),
               (4, 5, 1, 0), (1, 5, 7, 2), (4, 0, 3, 6))

    __colors = ((0, 0, 1), (0, 1, 1), (1, 1, 1),
                (1, 1, 0), (1, 0, 0), (1, 0, 1))

    __line_color = (0.3, 0.6, 0.5)

    def __init__(self, center, size):
        self.__center = center
        coord = size / 2
        self.__vertices = (
            (coord, -coord, -coord), (coord, coord, -coord),
            (-coord, coord, -coord), (-coord, -coord, -coord),
            (coord, -coord, coord), (coord, coord, coord),
            (-coord, -coord, coord), (-coord, coord, coord)
        )

    def draw(self, shift, fill, paint_function, scale=1.0, angle_x=0, angle_y=0, angle_z=0):
        self.__center[0] += shift[0]
        self.__center[1] += shift[1]

        glLoadIdentity()
        glPushMatrix()

        glTranslatef(*self.__center)
        glScalef(scale, scale, scale)
        glRotatef(angle_x, 1, 0, 0)
        glRotatef(angle_y, 0, 1, 0)
        glRotatef(angle_z, 0, 0, 1)

        if fill:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        glBegin(GL_QUADS)
        for i in range(len(self.__sides)):
            if fill:
                paint_function(self.__colors[i])
            else:
                paint_function(self.__line_color)

            for vertex in self.__sides[i]:
                glVertex3f(*self.__vertices[vertex])
        glEnd()

        glPopMatrix()


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

    def __compute_all(self):
        self.__compute_grid(self.__segments_count)
        self.__compute_normals()

    def __init__(self, vertices, center, segments_count=40):
        self.__center = center
        self.__vertices = vertices
        self.__segments_count = segments_count
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

    def draw(
            self, shift, fill, scale=1.0, angle_x=0, angle_y=0, angle_z=0,
            with_texture=False, with_lightning=False
    ):
        self.__center[0] += shift[0]
        self.__center[1] += shift[1]

        glLoadIdentity()
        glPushMatrix()

        glTranslatef(*self.__center)
        glScalef(scale, scale, scale)
        glRotatef(angle_x, 1, 0, 0)
        glRotatef(angle_y, 0, 1, 0)
        glRotatef(angle_z, 0, 0, 1)

        if fill:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        if with_texture:
            glEnable(GL_TEXTURE_2D)
        else:
            glDisable(GL_TEXTURE_2D)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnable(GL_NORMALIZE)

        if with_texture:
            glTexCoordPointer(2, GL_FLOAT, 0, self.__texture_coordinates * len(self.__grid))
        if with_lightning:
            glNormalPointer(GL_FLOAT, 0, self.__normals)
        glVertexPointer(3, GL_FLOAT, 0, self.__grid)
        glDrawArrays(GL_QUADS, 0, int(len(self.__grid) * 4))

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)

        glPopMatrix()
