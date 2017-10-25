# cython vectorbase.pyx
# gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o vectorbase.so vectorbase.c


cdef class VectorBase:
    cdef public double x, y, z

    def __add__(self, other):
        vb = VectorBase()
        vb.x = self.x + other.x
        vb.y = self.y + other.y
        vb.z = self.z + other.z
        return vb

    def __neg__(self):
        vb = VectorBase()
        vb.x = -self.x
        vb.y = -self.y
        vb.z = -self.z
        return vb

    def __sub__(self, other):
        vb = VectorBase()
        vb.x = self.x - other.x
        vb.y = self.y - other.y
        vb.z = self.z - other.z
        return vb

    def scale(self, other):
        vb = VectorBase()
        vb.x = self.x * other
        vb.y = self.y * other
        vb.z = self.z * other
        return vb

    def length(self):
        return (self.x * self.x + self.y * self.y + self.z * self.z) ** .5

    def normal(self):
        m = 1. / (self.x * self.x + self.y * self.y + self.z * self.z) ** .5
        vb = VectorBase()
        vb.x = self.x * m
        vb.y = self.y * m
        vb.z = self.z * m
        return vb

    def dot(self, other):
        return (self.x * other.x + self.y * other.y + self.z * other.z)

    def cross(self, other):
        vb = VectorBase()
        vb.x = self.y * other.z - self.z * other.y
        vb.y = self.z * other.x - self.x * other.z
        vb.z = self.x * other.y - self.y * other.x
        return vb
