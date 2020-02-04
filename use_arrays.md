# Let's use arrays and C code

Let's use Python's array module (or maybe the structs module, it remains to be
seen which is more appropriate). One is an array of floats (C: doubles) to
represent the positions of the ends of the edges. These approximate the
vertices so we want an array of those also. For a dodecahedron with 20
vertices, the vertex array will need 60 floats, and for the edge endpoints
we'll have 3 * 30 edges = 90 floats.

Let's think about how to generatlize this. You have N vertices, and a bunch
of edges, and each edge involves two vertices, so it has indices 0..N-1 into
the vertex array. Those indices are integers. Each edge also has two endpoints
which are 3-float points like the vertices.

You want the ctypes module for this. You build structs like this.

    from ctypes import *
    class POINT(Structure):
        _fields_ = ("x", c_int), ("y", c_int)

    class MyStruct(Structure):
        _fields_ = [("a", c_int),
                    ("b", c_float),
                    ("point_array", POINT * 4)]

    print len(MyStruct().point_array)


