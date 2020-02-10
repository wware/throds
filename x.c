// https://www.cprogramming.com/tutorial/shared-libraries-linux-gcc.html
// https://dbader.org/blog/python-ctypes-tutorial
// https://dbader.org/blog/python-ctypes-tutorial-part-2
// gcc -Wall -O2 -c x.c ; gcc -shared -o x.so x.o

/* Passing structs to functions by value in C - bad idea?
   https://stackoverflow.com/questions/161788 */

#include <stdio.h>
#include <stdlib.h>
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

/**
    def errf(self):
        def per_vertex(edge1, edge2, edge3, vertex):
            subtotal = 0.
            for e in (edge1, edge2, edge3):
                x = vec_sub(e._end1, e._end2)
                t = vec_dot(vertex, x)
                x = vec_scale(t, x)
                y = vec_sub(vertex, x)
                ylen = vec_len(y)
                subtotal += 10 * (ylen - (.5 * ROD_DIAM + 0.2)) ** 2
                if t > .5:
                    closer = e._end1
                else:
                    closer = e._end2
                dist = vec_sub(vertex, closer)
                subtotal += vec_dot(dist, dist)
            return subtotal

        edges_by_vertex = {}
        for e in self._edges:
            v1, v2 = e._vertex1, e._vertex2
            if v1 not in edges_by_vertex:
                edges_by_vertex[v1] = set()
            if v2 not in edges_by_vertex:
                edges_by_vertex[v2] = set()
            edges_by_vertex[v1].add(e)
            edges_by_vertex[v2].add(e)
        total = 0.
        for v in edges_by_vertex.keys():
            assert len(edges_by_vertex[v]) == 3
            e1, e2, e3 = edges_by_vertex[v]
            total += per_vertex(e1, e2, e3, v)
        return total
**/

struct list_link {
    struct list_link *next;
    int direction;
    Edge *edge;
};

struct list_link add_to_list(struct list_link *previous, int dir, Edge *e)
{
    struct list_link r = { previous, dir, e };
    return r;
}

double errf(Shape *shape)
{
    struct list_link this, **edges_per_vertex;
    int i;
    edges_per_vertex = malloc(shape->num_vertices * sizeof(struct list_link *));
    if (edges_per_vertex == NULL) {
        fprintf(stderr, "Out of memory!\n");
        exit(1);
    }
    for (i = 0; i < shape->num_vertices; i++) {
        edges_per_vertex[i] = NULL;
        this = add_to_list(edges_per_vertex[i]);
    }
}
