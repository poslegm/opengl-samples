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

    def __init__(self, vertices, center, segments_count=40):
        self.__center = center
        self.__vertices = vertices
        self.__segments_count = segments_count
        self.__compute_grid(segments_count)

    def change_line(self, vertices):
        if vertices != self.__vertices:
            self.__vertices = vertices
            self.__compute_grid(self.__segments_count)

    def change_segments_count(self, segments_count):
        if segments_count != self.__segments_count:
            self.__segments_count = segments_count
            self.__compute_grid(self.__segments_count)

    def draw(self, shift, fill, scale=1.0, angle_x=0, angle_y=0, angle_z=0):
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

        for polygon in self.__grid:
            glBegin(GL_POLYGON)
            for v in polygon:
                glVertex3f(*v)
            glEnd()

        glPopMatrix()
