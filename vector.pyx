# cython vector.pyx
# gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o vector.so vector.c

import random
from math import sin, cos


cdef class Vector:

    cdef public double x, y, z

    @classmethod
    def random(cls, size):
        return cls(
            (2 * random.random() - 1) * size,
            (2 * random.random() - 1) * size,
            (2 * random.random() - 1) * size
        )

    def __init__(self, x=None, y=None, z=None):
        if x is None:
            self.x = self.y = self.z = 0.
        elif y is None:
            self.x, self.y, self.z = x.x, x.y, x.z
        else:
            self.x, self.y, self.z = x, y, z

    def __add__(self, other):
        vb = Vector()
        vb.x = self.x + other.x
        vb.y = self.y + other.y
        vb.z = self.z + other.z
        return vb

    def __neg__(self):
        vb = Vector()
        vb.x = -self.x
        vb.y = -self.y
        vb.z = -self.z
        return vb

    def __sub__(self, other):
        vb = Vector()
        vb.x = self.x - other.x
        vb.y = self.y - other.y
        vb.z = self.z - other.z
        return vb

    def __mul__(self, other):
        # http://docs.cython.org/en/latest/src/userguide/special_methods.html#arithmetic-methods
        if isinstance(self, Vector):
            return self.dot(other)
        elif isinstance(self, (int, float)):
            vb = Vector()
            vb.x = other.x * self
            vb.y = other.y * self
            vb.z = other.z * self
            return vb
        else:
            return NotImplemented

    def length(self):
        return (self.x * self.x + self.y * self.y + self.z * self.z) ** .5

    def normal(self):
        m = 1. / (self.x * self.x + self.y * self.y + self.z * self.z) ** .5
        vb = Vector()
        vb.x = self.x * m
        vb.y = self.y * m
        vb.z = self.z * m
        return vb

    def dot(self, other):
        return (self.x * other.x + self.y * other.y + self.z * other.z)

    def cross(self, other):
        vb = Vector()
        vb.x = self.y * other.z - self.z * other.y
        vb.y = self.z * other.x - self.x * other.z
        vb.z = self.x * other.y - self.y * other.x
        return vb

    def to_list(self):
        return [self.x, self.y, self.z]

    @classmethod
    def from_array(cls, ary):
        return cls(*[float(x) for x in ary])

    def format(self, fmtstr):
        return fmtstr.format(self.x, self.y, self.z)

    def nudge(self, index, amount):
        if index == 0:
            return self + Vector(amount, 0, 0)
        elif index == 1:
            return self + Vector(0, amount, 0)
        elif index == 2:
            return self + Vector(0, 0, amount)
        else:
            raise ValueError((self, index, amount))

    def distance(self, other):
        return (self - other).length()

    def rotate(self, t):
        # rotation about a vector
        theta = t.length()
        delta = (self.dot(t) / t.dot(t)) * t
        u = self - delta
        v = (1. / theta) * t.cross(u)
        return Vector(cos(theta) * u + sin(theta) * v) + delta

    def make_translate(self):
        return self.format('translate([{0}, {1}, {2}])')
