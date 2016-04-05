from OpenGL.GL import *
import math


class Cube:
    __sides = ((0, 1, 2, 3), (3, 2, 7, 6), (6, 7, 5, 4),
               (4, 5, 1, 0), (1, 5, 7, 2), (4, 0, 3, 6))

    __colors = ((0, 0, 1, 1), (0, 1, 1, 1), (1, 1, 1, 1),
                (1, 1, 0, 1), (1, 0, 0, 1), (1, 0, 1, 1))

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

        glBegin(GL_QUADS)
        for i in range(len(self.__sides)):
            if fill:
                glColor4f(*self.__colors[i])
            else:
                glColor3f(*self.__line_color)
            for vertex in self.__sides[i]:
                glVertex3f(*self.__vertices[vertex])
        glEnd()

        glPopMatrix()


class SurfaceOfRevolution:
    def __get_delta(self, segmentsCount, i, r):
        angle = 2.0 * math.pi * i / segmentsCount
        dx = r * math.cos(angle)
        dz = r * math.sin(angle)
        return dx, dz

    def __draw_polygon(self, v1, v2, segmentsCount):
        r1 = math.sqrt(v1[0] ** 2 + v1[2] ** 2)
        r2 = math.sqrt(v2[0] ** 2 + v2[2] ** 2)

        for i in range(segmentsCount):
            glBegin(GL_POLYGON)
            dx1, dz1 = self.__get_delta(segmentsCount, i, r1)
            dx2, dz2 = self.__get_delta(segmentsCount, i, r2)

            glVertex3f(0.0 + dx1, v1[1], 0.0 + dz1)
            glVertex3f(0.0 + dx2, v2[1], 0.0 + dz2)

            dx1, dz1 = self.__get_delta(segmentsCount, i + 1, r1)
            dx2, dz2 = self.__get_delta(segmentsCount, i + 1, r2)

            glVertex3f(0.0 + dx2, v2[1], 0.0 + dz2)
            glVertex3f(0.0 + dx1, v1[1], 0.0 + dz1)

            glEnd()

    def __init__(self, vertices, center):
        self.__center = center
        self.__vertices = vertices

    def draw(self, shift, fill, scale=1.0, angle_x=0, angle_y=0, angle_z=0, segmentsCount=40):
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

        i = 0
        while i < len(self.__vertices) - 1:
            self.__draw_polygon(self.__vertices[i], self.__vertices[i + 1], segmentsCount)
            i += 1

        glPopMatrix()