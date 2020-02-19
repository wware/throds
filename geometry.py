import logging
import random
import unittest
from math import atan2, pi
# pylint: disable=no-name-in-module
from vector import Vector
# pylint: enable=no-name-in-module
from mechlib import (
    Translate, Rotate, Color, Hide,
    Cylinder, Container, Difference, Text
)

debugging = logging.getLogger().isEnabledFor(logging.DEBUG)

minimal_distance = 6.35

INCH = 25.4

# the sleeve is the solid thing that wraps around the threaded rod
# how long is the sleeve?
SLEEVE = 2 * INCH

# how far does the physical threaded rod extend beyond the center of
# the sleeve? this should be half the sleeve length, plus some more
# for nut and possible washers
EXTEND = 1.5 * INCH


class Rod(Container):
    def __init__(self, v1, v2):
        Container.__init__(self)
        if not isinstance(v1, Vector):
            raise TypeError(v1)
        if not isinstance(v2, Vector):
            raise TypeError(v2)
        self.v1, self.v2 = self._original_vertices = (v1, v2)
        self._ideal_vdist = (v2 - v1).length()
        self._original_midpoint = 0.5 * (v1 + v2)
        self.label1 = self.label2 = None

    def nearest_distance(self, other):
        if isinstance(other, Rod):
            e = self.delta.cross(other.delta).normal()
            return abs((self.v1 - other.v1).dot(e))
        raise TypeError(other)

    def shares_vertex_with(self, other):
        yours = (other.v1, other.v2)
        for mine in (self.v1, self.v2):
            if mine in yours:
                return True
        return False

    @property
    def extend(self):
        # how far does the rod extend beyond the nominal axis
        return EXTEND

    @property
    def sleeve(self):
        # how long is the sleeve
        return SLEEVE

    @property
    def width(self):
        # how wide should the hole be?
        # 1/4-20 thread => 1/4" plus a little elbow room
        elbow_room = 0.02
        return INCH * (0.25 + elbow_room)

    @property
    def swidth(self):
        # how wide should the sleeve be?
        # return INCH * 0.75
        return INCH * 0.5

    @property
    def original_vertices(self):
        return self._original_vertices

    @property
    def length(self):
        return self.delta.length() + 2 * self.extend

    @property
    def vdist_delta(self):
        return self.delta.length() - self._ideal_vdist

    @property
    def delta(self):
        return self.v2 - self.v1

    @property
    def midpoint(self):
        return 0.5 * (self.v1 + self.v2)

    @property
    def midpoint_drift(self):
        return (self.midpoint - self._original_midpoint).length()

    @property
    def end1(self):
        return self.v1 - self.extend * self.delta.normal()

    @property
    def end2(self):
        return self.v2 + self.extend * self.delta.normal()

    def parts_cylinder(self, center, length, diam, label=None):
        # handle rotation to make the cylinder parallel to this rod
        kCrossDelta = Vector(0, 0, 1).cross(self.delta)
        theta = atan2(kCrossDelta.length(), self.delta.z) * 180 / pi

        return Translate(center).containing(
            Rotate(theta=theta, vector=kCrossDelta).containing(
                self.addText(
                    Translate(0, 0, -.5 * length).containing(
                        Cylinder(h=length, d=diam)
                    ),
                    diam,
                    label
                )
            )
        )

    def addText(self, part, diam, label):
        if label is None:
            return part
        else:
            return Difference.has(part, self.prepareText(diam, label))

        # c = self.prepareText(diam, label)
        # if c is None:
        #     return part
        # else:
        #     return Difference.has(part, c)

    def prepareText(self, diam, label):
        assert diam < 20
        if label is None:
            return None
        c = Container()
        for angle in (0, 90, 180, 270):
            c.add(
                Rotate(theta=angle, vector=[0, 0, 1]).containing(
                    Translate(-2.5, 0.5 * diam, 0).containing(
                        Rotate(theta=-90, vector=[0, 1, 0]).containing(
                            Rotate(theta=-90, vector=[1, 0, 0]).containing(
                                Text(label)
                            )
                        )
                    )
                )
            )
        return c

    def D(self, dct, dct2, dct3):
        v1, v2 = self.original_vertices
        if v1 not in dct:
            dct[v1] = []
        if v2 not in dct:
            dct[v2] = []
        shell1 = self.parts_shell1().openscad()
        shell2 = self.parts_shell2().openscad()
        if shell1 not in dct[v1]:
            dct[v1].append(shell1)
        if shell2 not in dct[v2]:
            dct[v2].append(shell2)
        dct2[v1] = v1
        dct2[v2] = v2
        cutout = self.parts_cutout().openscad()
        if v1 not in dct3:
            dct3[v1] = []
        if v2 not in dct3:
            dct3[v2] = []
        if cutout not in dct3[v1]:
            dct3[v1].append(cutout)
        if cutout not in dct3[v2]:
            dct3[v2].append(cutout)

    def parts_shell1(self):
        return self.parts_cylinder(
            self.v1,
            self.sleeve,
            self.swidth,
            self.label1
        )

    def parts_shell2(self):
        return self.parts_cylinder(
            self.v2,
            self.sleeve,
            self.swidth,
            self.label2
        )

    def parts_shell(self):
        return Container.has(
            self.parts_shell1(),
            self.parts_shell2()
        )

    def parts_cutout(self):
        return self.parts_cylinder(
            self.midpoint,
            self.length,
            self.width
        )


class RodTest(unittest.TestCase):
    # Regrettably, these are really manual tests that I haven't found a
    # smart way to automate yet.

    def test1(self):
        v1 = Vector(0, 0, 0)
        v2 = Vector(1, 0, 1)
        r = Rod(v1, v2)
        r.prepareText(r.swidth, 'ABCD').openscad()  # assign this to a variable
        # Write it to a scad file and examine it in OpenSCAD.


class RodGraph(Container):
    def __init__(self):
        Container.__init__(self)
        self.innards()

    def innards(self):
        def correct_rod_length(i):
            def f():
                rod = self.rods()[i]
                dsq = rod.vdist_delta ** 2
                return 10 * dsq
            return f

        def hug_vertex(i, j):
            def f():
                rod, vertex = self.rods()[i], self.vertices()[j]
                d1 = (rod.v1 - vertex).length()
                d2 = (rod.v2 - vertex).length()
                return 10 * min(d1, d2)
            return f

        def avoid_overlap(i, j):
            def f():
                rod1, rod2 = self.rods()[i], self.rods()[j]
                inter_rod_distance = rod1.nearest_distance(rod2)
                retval = None
                points = [
                    (0, 10000),
                    (1.05 * minimal_distance, 0)
                ]
                for k in range(len(points) - 1):
                    this, this_value = points[k]
                    nxt, next_value = points[k+1]
                    if this <= inter_rod_distance <= nxt:
                        a = (
                            (1. * inter_rod_distance - this) /
                            (1. * nxt - this)
                        )
                        retval = this_value + a * (next_value - this_value)
                if retval is None:
                    retval = points[-1][1]
                # logging.debug(retval)
                return retval
            return f

        def encourage_symmetry(i):
            def f():
                rod = self.rods()[i]
                return 1 * rod.midpoint_drift ** 2
            return f

        self._rods = None
        self.terms = terms = []
        rods = self.rods()
        for i, r in enumerate(rods):
            terms.append(encourage_symmetry(i))
            terms.append(correct_rod_length(i))
            terms.append(hug_vertex(i, self.lookup_vertex(r.v1)))
            terms.append(hug_vertex(i, self.lookup_vertex(r.v2)))
            for j in range(i+1, len(rods)):
                r2 = rods[j]
                if r.shares_vertex_with(r2):
                    terms.append(avoid_overlap(i, j))

    def lookup_vertex(self, v):
        for i, vert in enumerate(self.vertices()):
            if v == vert:
                return i
        assert False, 'vertex not found'

    def twist(self, d):
        for r in self.rods():
            mid = r._original_midpoint
            w = mid.cross(r.v1 - mid)
            delta = (d / w.length()) * w
            r.v1 += delta
            r.v2 -= delta

    def to_list(self):
        lst = []
        for r in self.rods():
            lst.extend(r.v1.to_list() + r.v2.to_list())
        return lst

    def from_list(self, lst):
        assert len(lst) == 6 * len(self.rods())
        for i, r in enumerate(self.rods()):
            r.v1 = Vector.from_array(lst[6*i:6*i+3])
            r.v2 = Vector.from_array(lst[6*i+3:6*i+6])

    def wiggle(self):
        size = 2 * minimal_distance
        L = self.to_list()
        for i, _ in enumerate(L):
            L[i] += (2 * random.random() - 1) * size
        self.from_list(L)

    def fitness(self, L):
        self.from_list(L)
        _sum = 0.
        for f in self.terms:
            _sum += f() ** 2
        return _sum ** .5

    def vertices(self):
        return []

    def edges(self):
        return []

    def rods(self):
        if self._rods is None:
            verts = self.vertices()
            logging.debug(verts)
            self._rods = []
            i = 0
            for v1, v2 in self.edges():
                r = Rod(verts[v1], verts[v2])
                r.label1 = "{0}_>".format(i)
                r.label2 = "<_{0}".format(i)
                self._rods.append(r)
                i += 1
        return self._rods

    def parts_positive(self):
        return Container.has(
            *[x.parts_shell() for x in self.rods()]
        )

    def parts_negative(self):
        return Container.has(
            *[x.parts_cutout() for x in self.rods()]
        )

    def openscad(self):
        return Container.has(
            Hide.has(Color(1, 0, 0).containing(
                self.parts_negative()
            )),
            Difference.has(
                self.parts_positive(),
                self.parts_negative()
            )
        ).openscad()


class RodGraphTest(unittest.TestCase):
    class TestGraph(RodGraph):
        def vertices(self):
            return [
                Vector(0, 0, 0),
                Vector(1, 0, 0),
                Vector(0, 1, 0)
            ]

        def edges(self):
            return [
                (0, 1), (0, 2), (1, 2)
            ]

    def test1(self):
        # tg = self.TestGraph()
        # pos = tg.openscad_positive()
        # neg = tg.openscad_negative()
        self.assertTrue(True)    # put in a real test here some day
