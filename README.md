# Threaded rod design tool

![Image of tetrahedron](/tetra.jpg?raw=true "Optional Title")

This is a software design tool for Rep-Rap-style construction using threaded rods
(cheaply available at many hardware stores, or online) and 3d-printed plastic blocks.
This is in a very early stage of development and likely to be buggy and cantankerous
and frankly a bit user-hostile.

## Further work

I'm trying to get this thing to handle symmetries such as you might see in a Platonic
solid like a tetrahedron or a cube. Each vertex should be a rotation of its neighbors.
Unfortunately it requires re-thinking how graphs are specified. For each vertex you
need to assign an order to the rods, so that you can find correspondences between one
rod at one vertex and another rod at another vertex.

Let's rethink graph specifications. They should still be in Python but they should
minimize their dependence upon the code.

    center = (0, 0, 0.5)
    tetrahedron = graph(
        # locations of vertices        # edges, in order
        (1, 0, 0),                     (0, 1, 2),
        (-1, 0, 0),                    (0, 3, 4),
        (0, 1, 1),                     (1, 4, 5),
        (0, -1, 1),                    (2, 3, 5),
        symmetries={
            rot(center, 0, 1),
            rot(center, 0, 2),
            rot(center, 0, 3)
        }
    )

Let's see if that works better. There are two kinds of symmetries, rotations (`rot`)
and reflections (`refl`). A rotation requires the specification of a point about
which the rotation is done, such as the center of the tetrahedron. A reflection requires
the specification of a plane (a point, and a normal vector), like a mirror.

    xplane = plane((0, 0, 0), (1, 0, 0))
    yplane = plane((0, 0, 0), (0, 1, 0))
    zplane = plane((0, 0, 0), (0, 0, 1))
    cube = graph(
        (1, 1, 1),   ...
        (1, 1, -1),  ...
        (1, -1, 1),  ...
        ...
        symmetries={
            refl(zplane, 0, 1),
            refl(zplane, 2, 3),
            refl(yplane, 0, 2),
            ...
        }
    )

Needs more thinking but it looks like a start.
