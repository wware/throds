import ctypes

lib = ctypes.CDLL("./x.so")


def wrap_function(funcname, restype, argtypes):
    func = lib.__getattr__(funcname)
    func.restype = restype
    func.argtypes = argtypes
    return func


class Vector(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
        ("z", ctypes.c_double)
    ]

    def __init__(self, x, y, z):
        ctypes.Structure.__init__(self)
        self.x = x
        self.y = y
        self.z = z

        self._dot_func = wrap_function(
            'dot', ctypes.c_double,
            [ctypes.POINTER(Vector), ctypes.POINTER(Vector)]
        )
        self._cross_func = wrap_function(
            'cross', Vector,
            [ctypes.POINTER(Vector), ctypes.POINTER(Vector)]
        )
        self._linear_func = wrap_function(
            'linear', Vector,
            [ctypes.c_double, ctypes.POINTER(Vector),
             ctypes.c_double, ctypes.POINTER(Vector)]
        )

    def __repr__(self):
        return '({0}, {1}, {2})'.format(self.x, self.y, self.z)

    def __neg__(self):
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
print "======"


class Shape(ctypes.Structure):
    _fields_ = [
        ("num_vertices", ctypes.c_int),
        ("vertices", ctypes.POINTER(Vector)),
        ("num_edges", ctypes.c_int),
        ("edges", ctypes.POINTER(Edge))
    ]


class Tetrahedron(Shape):
    def __init__(self):
        Shape.__init__(self)
        self.num_vertices = 4
        vertices = a, b, c, d = (
            Vector(1, 0, -1),
            Vector(-1, 0, -1),
            Vector(1, 0, 1),
            Vector(-1, 0, 1)
        )
        self.vertices = (Vector * 4)(*vertices)
        self.num_edges = 6
        self.edges = (Edge * 6)(*(
            (0, 1, a, b),
            (0, 2, a, c),
            (0, 3, a, d),
            (1, 2, b, c),
            (1, 3, b, d),
            (2, 3, c, d)
        ))


# void print_shape(Shape *shape)
_print_shape = wrap_function(
    'print_shape', None,
    [ctypes.POINTER(Shape)]
)


s = Tetrahedron()
print s.vertices[1]

_print_shape(s)
