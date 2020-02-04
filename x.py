from ctypes import *

class POINT(Structure):
    _fields_ = ("x", c_double), ("y", c_double), ("z", c_double)

class EDGE(Structure):
    _fields_ = [("v1", c_int),
                ("v2", c_int),
                ("end1", POINT),
                ("end2", POINT)]

lib = CDLL("./x.so")
print lib.dot

VEC = lib.Vector

func = lib.dot
func.argtypes = POINT, POINT

u = POINT()
v = POINT()
u.x, u.y, u.z = 1, 2, 3
v.x, v.y, v.z = 2, 3, 5

