// https://www.cprogramming.com/tutorial/shared-libraries-linux-gcc.html
// https://dbader.org/blog/python-ctypes-tutorial
// https://dbader.org/blog/python-ctypes-tutorial-part-2
// gcc -Wall -O2 -c x.c ; gcc -shared -o x.so x.o

/* Passing structs to functions by value in C - bad idea?
   https://stackoverflow.com/questions/161788 */

#include <stdio.h>
#include "Python.h"

typedef struct {
    double x, y, z;
} Vector;

typedef struct {
    int v1;
    int v2;
    Vector end1;
    Vector end2;
} Edge;

PyMODINIT_FUNC
initx(void)
{
    (void) Py_InitModule("x", NULL);
}

Vector linear(double a, Vector *v1, double b, Vector *v2)
{
    Vector v = {
        a * v1->x + b * v2->x,
        a * v1->y + b * v2->y,
        a * v1->z + b * v2->z
    };
    return v;
}

double dot(Vector *v1, Vector *v2)
{
    return v1->x * v2->x +
           v1->y * v2->y +
           v1->z * v2->z;
}

Vector cross(Vector *v1, Vector *v2)
{
    Vector v = {
        v1->y * v2->z - v1->z * v2->y,
        v1->z * v2->x - v1->x * v2->z,
        v1->x * v2->y - v1->y * v2->x
    };
    return v;
}

typedef struct {
    int num_vertices;
    Vector *vertices;
    int num_edges;
    Edge *edges;
} Shape;

void print_shape(Shape *shape)
{
    int i;
    printf("%d %d\n", shape->num_vertices, shape->num_edges);
    for (i = 0; i < shape->num_vertices; i++)
        printf("%lf %lf %lf\n", shape->vertices[i].x, shape->vertices[i].y, shape->vertices[i].z);
    for (i = 0; i < shape->num_edges; i++) {
        Edge *e = &shape->edges[i];
        printf("%d %d\n", e->v1, e->v2);
        printf("%lf %lf %lf\n", e->end1.x, e->end1.y, e->end1.z);
    }
}
