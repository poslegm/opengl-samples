from OpenGL.GL import *
import math


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

    def draw(self, shift, fill, scale=1.0, angle_x=0, angle_y=0):
        self.__center[0] += shift[0]
        self.__center[1] += shift[1]

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


class SurfaceOfRevolution:
    @staticmethod
    def __draw_circle_around_y(x, y, z, r, segmentsCount):
        glBegin(GL_LINE_LOOP)
        for i in range(segmentsCount):
            angle = 2.0 * math.pi * i / segmentsCount
            dx = r * math.cos(angle)
            dz = r * math.sin(angle)
            glVertex3f(x + dx, y, z + dz)
        glEnd()

    def __init__(self, vertices, center):
        self.__center = center
        self.__vertices = vertices

    def draw(self, shift, fill, scale=1.0, angle_x=0, angle_y=0):
        self.__center[0] += shift[0]
        self.__center[1] += shift[1]

        glLoadIdentity()
        glPushMatrix()

        glTranslatef(*self.__center)
        glScalef(scale, scale, scale)
        glRotatef(angle_x, 1, 0, 0)
        glRotatef(angle_y, 0, 1, 0)

        for v in self.__vertices:
            r = math.sqrt(v[0] ** 2 + v[2] ** 2)
            self.__draw_circle_around_y(0.0, v[1], 0.0, r, 90)

        glPopMatrix()