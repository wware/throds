INCH = 25.4;
$fn = 20;

module cyl(end1, end2, diam) {
    y = [end2[0] - end1[0], end2[1] - end1[1], end2[2] - end1[2]];
    translate(end1)
        rotate(-acos(y[2] / norm(y)), cross(y, [0, 0, 1]))
            cylinder(h=norm(y), d=0.1);
}

{% for c in cylinders %}
cyl({{ c.end1 }}, {{ c.end2 }}, {{ c.diam }});{% endfor %}
