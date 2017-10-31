import random
import sys
import logging
from math import pi
from geometry import Vector, RodGraph, INCH, EXTEND

logging.basicConfig(
    format='%(asctime)-15s  %(levelname)s  '
    '%(filename)s:%(lineno)d  %(message)s',
    level=(logging.DEBUG if ('--debug' in sys.argv[1:]) else logging.INFO)
)


class Tetrahedron(RodGraph):
    """
    from geometry import *
    print Tetrahedron(100).openscad()
    """
    def __init__(self, size):
        v0 = Vector(size, 0, 0)
        v1 = v0.rotate(Vector(0, 0, 2*pi / 3))
        v2 = v0.rotate(Vector(0, 0, 4*pi / 3))
        v3 = Vector(0, 0, size * 2**.5)
        center = 0.25 * (v0 + v1 + v2 + v3)
        self.v0 = v0 - center
        self.v1 = v1 - center
        self.v2 = v2 - center
        self.v3 = v3 - center
        RodGraph.__init__(self)

    def vertices(self):
        return [self.v0, self.v1, self.v2, self.v3]

    def edges(self):
        return [
            (0, 1), (0, 2), (0, 3),
            (1, 2), (1, 3),
            (2, 3)
        ]


class Octohedron(RodGraph):
    def __init__(self, size):
        x = (2 ** .5) * size
        self.v0 = Vector(0, 0, x)
        self.v1 = Vector(0, 0, -x)
        self.v2 = Vector(0, x, 0)
        self.v3 = Vector(0, -x, 0)
        self.v4 = Vector(x, 0, 0)
        self.v5 = Vector(-x, 0, 0)
        RodGraph.__init__(self)

    def vertices(self):
        return [self.v0, self.v1, self.v2, self.v3, self.v4, self.v5]

    def edges(self):
        return [
            (0, 2), (0, 3), (0, 4), (0, 5),
            (1, 2), (1, 3), (1, 4), (1, 5),
            (2, 4), (3, 4), (2, 5), (3, 5)
        ]


class Cube(RodGraph):
    def __init__(self, size):
        self.v0 = Vector(-.5*size, -.5*size, -.5*size)
        self.v1 = Vector(-.5*size, -.5*size, .5*size)
        self.v2 = Vector(-.5*size, .5*size, -.5*size)
        self.v3 = Vector(-.5*size, .5*size, .5*size)
        self.v4 = Vector(.5*size, -.5*size, -.5*size)
        self.v5 = Vector(.5*size, -.5*size, .5*size)
        self.v6 = Vector(.5*size, .5*size, -.5*size)
        self.v7 = Vector(.5*size, .5*size, .5*size)
        RodGraph.__init__(self)

    def vertices(self):
        return [
            self.v0, self.v1, self.v2, self.v3,
            self.v4, self.v5, self.v6, self.v7
        ]

    def edges(self):
        return [
            (0, 2), (2, 6), (6, 4), (4, 0),
            (4, 5), (6, 7), (0, 1), (2, 3),
            (1, 5), (5, 7), (7, 3), (1, 3)
        ]


# T = Tetrahedron(100)
# T = Cube(100)
# T = Tetrahedron(12 * INCH - 2 * EXTEND)
T = Octohedron(12 * INCH - 2 * EXTEND)


def simulated_anneal(func, initial, niter):

    def make_random(size):
        return [(2 * random.random() - 1) * size for _ in range(len(initial))]

    def add(lst1, lst2):
        return [x + y for x, y in zip(lst1, lst2)]

    x = initial
    f = func(x)
    N = niter * len(initial)
    size = 6.35
    mult = (0.01 / 6.35) ** (1. / N)
    for _ in range(N):
        delta = make_random(size)
        candidate = add(x, delta)
        f1 = func(candidate)
        if f1 < f:
            x = candidate
            f = f1
        size *= mult
    return x


def main():
    result = None
    result = simulated_anneal(T.fitness, T.to_list(), niter=500)
    T.from_list(result)

    template1 = """
intersection() {
    translate([-50, -50, -50])
        cube([100, 100, 100]);
    translate([0, 0, -%(vz)f]) {
        %(shape)s
    }
}
"""

    # This is if you want to print four at once.
    template2 = """
union() {
    %(shape)s
    translate([%(delta)f, 0, 0]) {
        %(shape)s
    }
    translate([0, %(delta)f, 0]) {
        %(shape)s
    }
    translate([%(delta)f, %(delta)f, 0]) {
        %(shape)s
    }
}
"""

    print "$fn = 20;"
    if '--pieces' in sys.argv[1:]:
        dct = {}
        dct2 = {}
        dct3 = {}
        for r in T.rods():
            r.D(dct, dct2, dct3)
        gap = 60
        offsets = [
            (0, 0), (gap, 0), (gap, gap), (0, gap)
        ]
        for key, offset in zip(dct.keys(), offsets):
            v = dct2[key]
            shells = dct[key]
            cutouts = dct3[key]
            print (
                (Vector(offset[0], offset[1], 0) - v).make_translate() +
                '\ndifference() {{\nunion() {{\n{0}\n}}\n'.format(
                    '\n'.join(shells)
                ) +
                'union() {\n' + '\n'.join(cutouts) + '\n}\n}'
            )
        sys.exit(0)

    T1 = T.openscad()

    if False:
        T1 = template1 % {'vz': T.v3.z, 'shape': T1}
    if False:
        T1 = template2 % {'delta': 45, 'shape': T1}
    print T1


if __name__ == '__main__':
    main()
