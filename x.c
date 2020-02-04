// https://www.cprogramming.com/tutorial/shared-libraries-linux-gcc.html
// https://dbader.org/blog/python-ctypes-tutorial
// https://dbader.org/blog/python-ctypes-tutorial-part-2
// gcc -Wall -c x.c ; gcc -shared -o x.so x.o

#include <stdio.h>

typedef struct vector {
	double x, y, z;
} Vector;

double dot(struct vector *v1, struct vector *v2)
{
	printf("%lf\n", v1->x);
	return (
		v1->x * v2->x +
		v1->y * v2->y +
		v1->z * v2->z
	);
}
