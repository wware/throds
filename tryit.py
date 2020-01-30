#!/usr/bin/env python

import os
import random
from jinja2 import Environment, BaseLoader


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

from math import pi, cos, sin


class vertices(object):
    def __init__(self, A, B):
        # assert 0 <= A <= 1
        # assert 0 <= B <= 1
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


K = 3
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

ROD_DIAM =  0.25

def vec_lin(a, x, b, y):
    return [a * x[0] + b * y[0],
            a * x[1] + b * y[1],
            a * x[2] + b * y[2]]
def vec_add(x, y):
    return vec_lin(1, x, 1, y)
def vec_sub(x, y):
    return vec_lin(1, x, -1, y)
def vec_scale(k, x):
    return vec_lin(k, x, 0, x)
def vec_dot(x, y):
    return x[0] * y[0] + x[1] * y[1] + x[2] * y[2]
def vec_cross(x, y):
    return [
        x[1] * y[2] - x[2] * y[1],
        x[2] * y[0] - x[0] * y[2],
        x[0] * y[1] - x[1] * y[0]
    ]


class Edge(object):
    def __init__(self, end1, end2):
        self._end1 = end1
        self._end2 = end2
    def cylinder(self):
        return dict(
            end1=self._end1,
            end2=self._end2,
            diam=ROD_DIAM
        )
    def nudge(self):
        center = vec_lin(.5, self._end1, .5, self._end2)
        span = vec_lin(1, self._end1, -1, center)
        h = vec_cross(center, span)
        hlensq = vec_dot(h, h)
        assert hlensq > 1.e-12, hlensq
        h = vec_scale(ROD_DIAM / hlensq**.5, h)
        return self.__class__(vec_add(self._end1, h), vec_sub(self._end2, h))


class Dodecahedron(object):
    def __init__(self, size=None):
        if size is None:
            return
        assert isinstance(size, (int, float)), size
        self.vertices = vertices = []
        step = pi * 72 / 180
        halfstep = .5 * step

        def foo(i):
            theta = i * step
            ra = size * (1 - A ** 2) ** .5
            rb = size * (1 - B ** 2) ** .5
            return theta, ra, rb

        for i in xrange(5):
            theta, ra, rb = foo(i)
            vertices.append([ra * cos(theta), ra * sin(theta), A * size])
        for i in xrange(5):
            theta, ra, rb = foo(i)
            vertices.append([rb * cos(theta), rb * sin(theta), B * size])
        for i in xrange(5):
            theta, ra, rb = foo(i + 0.5)
            vertices.append([rb * cos(theta), rb * sin(theta), -B * size])
        for i in xrange(5):
            theta, ra, rb = foo(i + 0.5)
            vertices.append([ra * cos(theta), ra * sin(theta), -A * size])

        self.cylinders = cylinders = []
        for i in xrange(5):
            Ea = vertices[i]
            E2a = vertices[(i + 1) % 5]
            Eb = vertices[i + 5]
            Fb = vertices[i + 10]
            F2b = vertices[((i + 4) % 5) + 10]
            Ga = vertices[i + 15]
            G2a = vertices[((i + 1) % 5) + 15]
            cylinders.append(Edge(Ea, Eb))
            cylinders.append(Edge(Ea, E2a))
            cylinders.append(Edge(Eb, Fb))
            cylinders.append(Edge(Eb, F2b))
            cylinders.append(Edge(Fb, Ga))
            cylinders.append(Edge(Ga, G2a))

    def nudge(self):
        clone = self.__class__()
        clone.cylinders = [x.nudge() for x in self.cylinders]
        clone.vertices = self.vertices
        return clone

    def data(self):
        return [e.cylinder() for e in self.cylinders]


rtemplate = Environment(loader=BaseLoader).from_string(
    open("template.scad").read()
)
open("z.scad", "w").write(rtemplate.render(dict(
    cylinders=Dodecahedron(size=12).nudge().data()
    # cylinders = Dodecahedron(size=12).data()
)))
os.system('openscad z.scad')
