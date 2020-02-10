#!/usr/bin/env python

import os
from math import pi, cos, sin
from jinja2 import Environment, BaseLoader
# pylint: disable=protected-access,redefined-outer-name,too-many-locals


# The top five vertices are at 72-degree increments at a height of z=A.
# The next five vertices are at the same 72-degree incremenets at a
# height of z=B. Next five are offset by 36 degrees, with z=-B, and last
# five are also offset by 36 degrees with z=-A. The trick is to make sure
# all the lengths are the same, and solve for A and B.
# Let Ea and Fa be two adjacent vertices of the top five. Let Eb and Fb
# be the vertices below them at z=B. Let Gb be the vertex connecting to
# Eb and Fb at z=-B, then you have
#     d = |Ea-Fa|^2 = |Ea-Eb|^2 = |Eb-Gb|^2 = |Fb-Gb|^2
# Then we can just set up an error function of the differences between
# these four distances, and do gradient descent in A and B to make all
# the distances equal.
# Without loss of generality assume all vertices are distance 1 from the
# origin.


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
ROD_DIAM = 0.25

for _ in xrange(10000):
    v1 = vertices(A, B)
    v2 = vertices(A + h, B)
    v3 = vertices(A, B + h)
    partialA = (v2.error() - v1.error()) / h
    partialB = (v3.error() - v1.error()) / h
    A -= m * partialA
    B -= m * partialB


def vec_lin(a, x, b, y):
    return (a * x[0] + b * y[0],
            a * x[1] + b * y[1],
            a * x[2] + b * y[2])


def vec_add(x, y):
    return vec_lin(1, x, 1, y)


def vec_sub(x, y):
    return vec_lin(1, x, -1, y)


def vec_scale(k, x):
    return vec_lin(k, x, 0, x)


def vec_dot(x, y):
    return x[0] * y[0] + x[1] * y[1] + x[2] * y[2]


def vec_len(x):
    return vec_dot(x, x) ** .5


def vec_cross(x, y):
    return (
        x[1] * y[2] - x[2] * y[1],
        x[2] * y[0] - x[0] * y[2],
        x[0] * y[1] - x[1] * y[0]
    )


class Edge(object):
    def __init__(self, end1, end2):
        self._end1 = end1
        self._end2 = end2
        self._vertex1 = end1
        self._vertex2 = end2

    def cylinder(self):
        return dict(
            end1=list(self._end1),
            end2=list(self._end2),
            diam=ROD_DIAM
        )

    def nudge(self):
        center = vec_lin(.5, self._end1, .5, self._end2)
        span = vec_lin(1, self._end1, -1, center)
        h = vec_cross(center, span)
        hlensq = vec_dot(h, h)
        assert hlensq > 1.e-12, hlensq
        h = vec_scale(ROD_DIAM / hlensq**.5, h)
        r = self.__class__(vec_add(self._end1, h), vec_sub(self._end2, h))
        # keep _vertex1 and _vertex2 unmodified
        r._vertex1 = self._vertex1
        r._vertex2 = self._vertex2
        return r


class Dodecahedron(object):
    def __init__(self, size=None):
        if size is None:
            return
        assert isinstance(size, (int, float)), size
        self.vertices = vertices = []
        step = pi * 72 / 180

        def foo(i):
            theta = i * step
            ra = size * (1 - A ** 2) ** .5
            rb = size * (1 - B ** 2) ** .5
            return theta, ra, rb

        for i in xrange(5):
            theta, ra, rb = foo(i)
            vertices.append((ra * cos(theta), ra * sin(theta), A * size))
        for i in xrange(5):
            theta, ra, rb = foo(i)
            vertices.append((rb * cos(theta), rb * sin(theta), B * size))
        for i in xrange(5):
            theta, ra, rb = foo(i + 0.5)
            vertices.append((rb * cos(theta), rb * sin(theta), -B * size))
        for i in xrange(5):
            theta, ra, rb = foo(i + 0.5)
            vertices.append((ra * cos(theta), ra * sin(theta), -A * size))

        self._edges = edges = []
        for i in xrange(5):
            Ea = vertices[i]
            E2a = vertices[(i + 1) % 5]
            Eb = vertices[i + 5]
            Fb = vertices[i + 10]
            F2b = vertices[((i + 4) % 5) + 10]
            Ga = vertices[i + 15]
            G2a = vertices[((i + 1) % 5) + 15]
            edges.append(Edge(Ea, Eb))
            edges.append(Edge(Ea, E2a))
            edges.append(Edge(Eb, Fb))
            edges.append(Edge(Eb, F2b))
            edges.append(Edge(Fb, Ga))
            edges.append(Edge(Ga, G2a))

    def clone(self, f=None):
        def identity(x):
            return x

        if f is None:
            f = identity
        clone = self.__class__()
        clone._edges = [f(x) for x in self._edges]
        clone.vertices = self.vertices
        return clone

    def nudge(self, direction=None):
        if direction is not None:
            c = self.clone()
            n = len(self._edges)
            for i in range(n):
                c._edges[i]._end1 = vec_add(c._edges[i]._end1,
                                            direction[3*i:3*i+3])
            for i in range(len(self._edges)):
                c._edges[i]._end2 = vec_add(c._edges[i]._end2,
                                            direction[3*(i+n):3*(i+n)+3])
            return c
        else:
            return self.clone(lambda edge: edge.nudge())

    def data(self):
        return [e.cylinder() for e in self._edges]

    def errf(self):
        def per_vertex(edge1, edge2, edge3, vertex):
            subtotal = 0.
            for e in (edge1, edge2, edge3):
                x = vec_sub(e._end1, e._end2)
                t = vec_dot(vertex, x)
                x = vec_scale(t, x)
                y = vec_sub(vertex, x)
                ylen = vec_len(y)
                subtotal += 10 * (ylen - (.5 * ROD_DIAM + 0.2)) ** 2
                if t > .5:
                    closer = e._end1
                else:
                    closer = e._end2
                dist = vec_sub(vertex, closer)
                subtotal += vec_dot(dist, dist)
            return subtotal

        edges_by_vertex = {}
        for e in self._edges:
            v1, v2 = e._vertex1, e._vertex2
            if v1 not in edges_by_vertex:
                edges_by_vertex[v1] = set()
            if v2 not in edges_by_vertex:
                edges_by_vertex[v2] = set()
            edges_by_vertex[v1].add(e)
            edges_by_vertex[v2].add(e)
        total = 0.
        for v in edges_by_vertex.keys():
            assert len(edges_by_vertex[v]) == 3
            e1, e2, e3 = edges_by_vertex[v]
            total += per_vertex(e1, e2, e3, v)
        return total

    def partials(self):
        _partials = []
        clone = self.clone()
        epsilon = 1.e-6
        baseline = self.errf()
        print baseline
        units = [
            (epsilon, 0, 0), (0, epsilon, 0), (0, 0, epsilon)
        ]
        for i in range(len(self._edges)):
            for j in range(3):
                clone._edges[i]._end1 = vec_add(
                    clone._edges[i]._end1,
                    units[j]
                )
                _partials.append((clone.errf() - baseline) / epsilon)
        for i in range(len(self._edges)):
            for j in range(3):
                clone._edges[i]._end2 = vec_add(
                    clone._edges[i]._end2,
                    units[j]
                )
                _partials.append((clone.errf() - baseline) / epsilon)
        return _partials

    def minimize(self):
        h = 0.05
        c = self.clone()
        for i in xrange(200):
            print i
            p = self.partials()
            m = max([abs(x) for x in p])
            p = [-(h / m) * x for x in p]
            c = c.nudge(p)
            h *= 0.8
        print
        return c


rtemplate = Environment(loader=BaseLoader).from_string(
    open("template.scad").read()
)
dodec = Dodecahedron(size=12).nudge()
dodec = dodec.minimize()
open("z.scad", "w").write(rtemplate.render(dict(
    cylinders=dodec.data()
    # cylinders = Dodecahedron(size=12).data()
)))

# Linux
if os.system('openscad z.scad 2> /dev/null') != 0:
    # Mac
    os.system("$(locate OpenSCAD | grep -E '/OpenSCAD$') z.scad")
