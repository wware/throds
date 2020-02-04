import ctypes

lib = ctypes.CDLL("./x.so")


class Vector(ctypes.Structure):
    _fields_ = ("x", ctypes.c_double), ("y", ctypes.c_double), ("z", ctypes.c_double)

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

        def wrap_function(lib, funcname, restype, argtypes):
            func = lib.__getattr__(funcname)
            func.restype = restype
            func.argtypes = argtypes
            return func

        self._dot_func = wrap_function(
            lib, 'dot', ctypes.c_double,
            [ctypes.POINTER(Vector), ctypes.POINTER(Vector)]
        )
        self._cross_func = wrap_function(
            lib, 'cross', Vector,
            [ctypes.POINTER(Vector), ctypes.POINTER(Vector)]
        )
        self._linear_func = wrap_function(
            lib, 'linear', Vector,
            [ctypes.c_double, ctypes.POINTER(Vector), ctypes.c_double, ctypes.POINTER(Vector)]
        )

    def __repr__(self):
        return '({0}, {1}, {2})'.format(self.x, self.y, self.z)

    def __neg__(self, other):
        return self._linear_func(-1., self, 0., self)

    def __add__(self, other):
        return self._linear_func(1., self, 1., other)

    def __sub__(self, other):
        return self._linear_func(1., self, -1., other)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return self._linear_func(other, self, 0., self)
        elif isinstance(other, Vector):
            return self.dot(other)
        else:
            raise TypeError(type(other).__name__)

    def __rmul__(self, other):
        return self.__mul__(other)

    def scale(self, k):
        return self._linear_func(k, self, 0., self)

    def dot(self, other):
        return self._dot_func(self, other)

    def cross(self, other):
        return self._cross_func(self, other)

    @classmethod
    def tests(cls):
        u = cls(1, 2, 3)
        v = cls(4, 5, 6)
        print 9 * u
        print u * 7
        print u * v
        print u + v
        print v - u
        print u.cross(v)


class Edge(ctypes.Structure):
    _fields_ = [("v1", ctypes.c_int),
                ("v2", ctypes.c_int),
                ("end1", Vector),
                ("end2", Vector)]


Vector.tests()

class Shape(object):
    # Base shape is a tetrahedron, this is misshapen
    vertices = (
        Vector(1, 0, -1),
        Vector(-1, 0, -1),
        Vector(1, 0, 1),
        Vector(-1, 0, 1)
    )

    edges = (
        (0, 1), (0, 2), (0, 3),
        (1, 2), (1, 3), (2, 3)
    )



s = Shape()
print s.vertices[1]
