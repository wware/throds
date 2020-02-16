#!/usr/bin/env python

from math import pi, cos, sin


class AbstractMethod(NotImplementedError):
    pass


class ObjBuilder(object):
    # pylint: disable=unused-argument
    def add_vertex(self, vec):
        raise AbstractMethod()
    def add_edge(self, i, j):
        raise AbstractMethod()
    # pylint: enable=unused-argument


class HarmlessObjBuilder(ObjBuilder):
    def add_vertex(self, vec):
        print vec
    def add_edge(self, i, j):
        print i, j



def octahedron(size, objbuilder):
    assert isinstance(size, (int, float)), size
    assert isinstance(objbuilder, ObjBuilder), objbuilder
    d = (0.5 ** .5) * size
    objbuilder.add_vertex((0, 0, d))
    objbuilder.add_vertex((0, 0, -d))
    objbuilder.add_vertex((0, d, 0))
    objbuilder.add_vertex((0, -d, 0))
    objbuilder.add_vertex((d, 0, 0))
    objbuilder.add_vertex((-d, 0, 0))
    objbuilder.add_edge(0, 2)
    objbuilder.add_edge(0, 3)
    objbuilder.add_edge(0, 4)
    objbuilder.add_edge(0, 5)
    objbuilder.add_edge(1, 2)
    objbuilder.add_edge(1, 3)
    objbuilder.add_edge(1, 4)
    objbuilder.add_edge(1, 5)
    objbuilder.add_edge(2, 3)
    objbuilder.add_edge(3, 4)
    objbuilder.add_edge(4, 5)
    objbuilder.add_edge(5, 2)


def dodecahedron(size, objbuilder):
    # pylint: disable=too-many-locals
    assert isinstance(size, (int, float)), size
    assert isinstance(objbuilder, ObjBuilder), objbuilder
    step = pi * 72 / 180

    class vertices(object):
        """
        The top five vertices are at 72-degree increments at a height of z=A.
        The next five vertices are at the same 72-degree incremenets at a
        height of z=B. Next five are offset by 36 degrees, with z=-B, and last
        five are also offset by 36 degrees with z=-A. The trick is to make sure
        all the lengths are the same, and solve for A and B.
        Let Ea and Fa be two adjacent vertices of the top five. Let Eb and Fb
        be the vertices below them at z=B. Let Gb be the vertex connecting to
        Eb and Fb at z=-B, then you have
            d = |Ea-Fa|^2 = |Ea-Eb|^2 = |Eb-Gb|^2 = |Fb-Gb|^2
        Then we can just set up an error function of the differences between
        these four distances, and do gradient descent in A and B to make all
        the distances equal.
        Without loss of generality assume all vertices are distance 1 from the
        origin.
        """
        def __init__(self, A, B):
            self.A, self.B = A, B
            theta = pi * 72 / 180
            ra = (1 - A**2) ** .5
            rb = (1 - B**2) ** .5
            self.Ea = (ra, 0, A)
            self.Fa = (ra * cos(theta), ra * sin(theta), A)
            self.Eb = (rb, 0, B)
            self.Fb = (rb * cos(theta), rb * sin(theta), B)
            self.Gb = (rb * cos(.5*theta), rb * sin(.5*theta), -B)

        def error(self):
            def dist(p1, p2):
                return ((p1[0] - p2[0]) ** 2 +
                        (p1[1] - p2[1]) ** 2 +
                        (p1[2] - p2[2]) ** 2) ** .5
            d1 = dist(self.Ea, self.Fa)
            d2 = dist(self.Ea, self.Eb)
            d3 = dist(self.Eb, self.Gb)
            d4 = dist(self.Fb, self.Gb)
            return (d1 - d2) ** 2 + (d2 - d3) ** 2 + (d3 - d4) ** 2

    A, B = 0.8, 0.3
    h = 1.e-12
    m = 1.e-4

    for _ in xrange(10000):
        v1 = vertices(A, B)
        v2 = vertices(A + h, B)
        v3 = vertices(A, B + h)
        partialA = (v2.error() - v1.error()) / h
        partialB = (v3.error() - v1.error()) / h
        A -= m * partialA
        B -= m * partialB

    def foo(i):
        theta = i * step
        ra = size * (1 - A ** 2) ** .5
        rb = size * (1 - B ** 2) ** .5
        return theta, ra, rb

    for i in xrange(5):
        theta, ra, rb = foo(i)
        objbuilder.add_vertex((ra * cos(theta), ra * sin(theta), A * size))
    for i in xrange(5):
        theta, ra, rb = foo(i)
        objbuilder.add_vertex((rb * cos(theta), rb * sin(theta), B * size))
    for i in xrange(5):
        theta, ra, rb = foo(i + 0.5)
        objbuilder.add_vertex((rb * cos(theta), rb * sin(theta), -B * size))
    for i in xrange(5):
        theta, ra, rb = foo(i + 0.5)
        objbuilder.add_vertex((ra * cos(theta), ra * sin(theta), -A * size))

    for i in xrange(5):
        Ea = i
        E2a = (i + 1) % 5
        Eb = i + 5
        Fb = i + 10
        F2b = ((i + 4) % 5) + 10
        Ga = i + 15
        G2a = ((i + 1) % 5) + 15
        objbuilder.add_edge(Ea, Eb)
        objbuilder.add_edge(Ea, E2a)
        objbuilder.add_edge(Eb, Fb)
        objbuilder.add_edge(Eb, F2b)
        objbuilder.add_edge(Fb, Ga)
        objbuilder.add_edge(Ga, G2a)
    # pylint: disable=too-many-locals
