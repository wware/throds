import unittest
from math import pi
# pylint: disable=no-name-in-module
from vector import Vector
# pylint: enable=no-name-in-module


class VectorTest(unittest.TestCase):
    def approx(self, v1, v2):
        self.assertTrue(v1.distance(v2) < 1.e-6, (v1, v2))

    def test_simplest(self):
        # rotate a unit vector using a perpendicular angle vector
        u = Vector(1, 0, 0)
        self.approx(-1 * u, Vector(-1, 0, 0))
        self.approx(2 * u, Vector(2, 0, 0))
        self.approx(3 * u, Vector(3, 0, 0))

    def test_simple(self):
        # rotate a unit vector using a perpendicular angle vector
        u = Vector(1, 0, 0)
        self.approx(u.rotate(Vector(0, 0.01, 0)), Vector(0.99995, 0, -0.01))
        self.approx(u.rotate(Vector(0, pi/2, 0)), Vector(0, 0, -1))
        self.approx(u.rotate(Vector(0, pi, 0)), Vector(-1, 0, 0))
        self.approx(u.rotate(Vector(0, 3*pi/2, 0)), Vector(0, 0, 1))

    def test_2(self):
        # rotate a non-unit vector using a perpendicular angle vector
        u = Vector(1, 1, 0)
        self.approx(u.rotate(Vector(0, 0, pi/2)), Vector(-1, 1, 0))
        self.approx(u.rotate(Vector(0, 0, pi)), Vector(-1, -1, 0))
        self.approx(u.rotate(Vector(0, 0, 3*pi/2)), Vector(1, -1, 0))

    def test_3(self):
        # rotate a non-unit vector using a non-perpendicular angle vector
        u = Vector(1, 0, 1)
        self.approx(u.rotate(Vector(0, 0, pi/2)), Vector(0, 1, 1))
        self.approx(u.rotate(Vector(0, 0, pi)), Vector(-1, 0, 1))
        self.approx(u.rotate(Vector(0, 0, 3*pi/2)), Vector(0, -1, 1))


class Base(object):
    def __init__(self, x=0, y=0, z=0):
        if isinstance(x, Vector):
            # pylint: disable=no-member
            self.x, self.y, self.z = x.x, x.y, x.z
            # pylint: enable=no-member
        else:
            self.x, self.y, self.z = x, y, z

    def openscad(self):
        return self.__doc__.format(self.x, self.y, self.z) + ";"


class Container(Base):
    "union()"
    @classmethod
    def has(cls, *kids):
        # like "containing", but this also instantiates the container
        r = cls()
        r.containing(*kids)
        return r

    def __init__(self, *args, **kwargs):
        Base.__init__(self, *args, **kwargs)
        self.children = []

    def add(self, child):
        assert not isinstance(child, str)
        if child not in self.children:
            self.children.append(child)

    def containing(self, *kids):
        for kid in kids:
            self.add(kid)
        return self

    def openscad(self):
        r = Base.openscad(self)[:-1] + "{\n"
        r += "\n".join([c.openscad() for c in self.children])
        return r + "\n};"


class Color(Container):
    "color([{0}, {1}, {2}])"


class Intersection(Container):
    "intersection()"


class Difference(Container):
    "difference()"


class ContainerTest(unittest.TestCase):
    def test1(self):
        c = Container.has(
            Translate(1, 2, 3).containing(Rect(4, 5, 6)),
            Rotate(7, 8, 9, 10).containing(Rect(11, 12, 13))
        )
        self.assertEqual(
            c.openscad().replace("\n", "").replace(" ", ""),
            "union(){translate([1,2,3]){cube([4,5,6]);};"
            "rotate(10,[7,8,9]){cube([11,12,13]);};};"
        )


class Translate(Container):
    "translate([{0}, {1}, {2}])"


class Rotate(Container):
    def __init__(self, x=0, y=0, z=0, theta=0, vector=None):
        if vector is not None:
            if isinstance(vector, (list, tuple)):
                vector = apply(Vector, vector)
            Container.__init__(self, vector.x, vector.y, vector.z)
        else:
            Container.__init__(self, x, y, z)
        self.theta = theta

    def openscad(self):
        return (
            "rotate({0}, [{1}, {2}, {3}]) {{\n".format(
                self.theta, self.x, self.y, self.z
            ) +
            "\n".join([c.openscad() for c in self.children]) +
            "\n};"
        )


class Rect(Base):
    "cube([{0}, {1}, {2}])"


class Cylinder(Base):
    "cylinder([{0}, {1}, {2}])"

    # pylint: disable=super-init-not-called
    def __init__(self, h=1, d=1, r=None, d1=None, d2=None, r1=None, r2=None):
        self.h, self.d, self.r = h, d, r
        self.d1, self.d2 = d1, d2
        self.r1, self.r2 = r1, r2
    # pylint: enable=super-init-not-called

    def openscad(self):
        args = (
            "h={0}, r1={1}, r2={2}".format(self.h, self.r1, self.r2)
            if self.r1 is not None else
            (
                "h={0}, d1={1}, d2={2}".format(self.h, self.d1, self.d2)
                if self.d1 is not None else
                (
                    "h={0}, r={1}".format(self.h, self.r)
                    if self.r is not None else
                    "h={0}, d={1}".format(self.h, self.d)
                )
            )
        )
        return "cylinder(" + args + ");"


class Text(object):
    """
    translate([0, 0, -.5*{2}]) linear_extrude(height={2})
    {{text(text=\"{0}\", size={1}, halign=\"center\");}}
    """

    def __init__(self, text, size=5, height=3):
        self.text, self.size, self.height = text, size, height

    def openscad(self):
        return self.__doc__.format(self.text, self.size, self.height)


class Hide(Container):
    "%union()"
