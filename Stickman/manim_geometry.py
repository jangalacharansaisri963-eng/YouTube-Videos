from manim import *
import numpy as np


# ----- Coordinates -----

def point(x=0, y=0, z=0):
    return np.array([x, y, z], dtype=float)


def polar(r, theta, center=ORIGIN):
    return center + r * np.array([np.cos(theta), np.sin(theta), 0])


def midpoint(a, b):
    return (np.array(a) + np.array(b)) / 2


def distance(a, b):
    return np.linalg.norm(np.array(b) - np.array(a))


def unit(v):
    v = np.array(v, dtype=float)
    n = np.linalg.norm(v)
    return v / n if n else v


def lerp(a, b, t):
    return np.array(a) + (np.array(b) - np.array(a)) * t


def rotate_vector(v, angle):
    c, s = np.cos(angle), np.sin(angle)
    x, y, z = np.array(v)
    return np.array([c * x - s * y, s * x + c * y, z])


# ----- Basic Geometry -----

def line(a, b, **kwargs):
    return Line(a, b, **kwargs)


def segment(a, b, **kwargs):
    return Line(a, b, **kwargs)


def polygon(*vertices, **kwargs):
    return Polygon(*vertices, **kwargs)


def rectangle(width, height, **kwargs):
    return Rectangle(width=width, height=height, **kwargs)


def rounded_rectangle(width, height, corner_radius=0.2, **kwargs):
    return RoundedRectangle(
        width=width,
        height=height,
        corner_radius=corner_radius,
        **kwargs
    )


def circle(radius=1, **kwargs):
    return Circle(radius=radius, **kwargs)


def ellipse(width=2, height=1, **kwargs):
    return Ellipse(width=width, height=height, **kwargs)


def ring(outer_radius=1, inner_radius=0.7, **kwargs):
    return Annulus(
        inner_radius=inner_radius,
        outer_radius=outer_radius,
        **kwargs
    )


# ----- Angles and Arcs -----

def arc(radius=1, start=0, angle=TAU / 2, **kwargs):
    return Arc(
        radius=radius,
        start_angle=start,
        angle=angle,
        **kwargs
    )


def sector(radius=1, start=0, angle=TAU / 2, **kwargs):
    return Sector(
        radius=radius,
        start_angle=start,
        angle=angle,
        **kwargs
    )


def angle_arc(a, vertex, b, radius=0.4, **kwargs):
    va = unit(np.array(a) - vertex)
    vb = unit(np.array(b) - vertex)
    start = np.arctan2(va[1], va[0])
    end = np.arctan2(vb[1], vb[0])
    delta = (end - start) % TAU
    return Arc(
        radius=radius,
        start_angle=start,
        angle=delta,
        arc_center=vertex,
        **kwargs
    )


# ----- Polygons -----

def regular_polygon(n, radius=1, **kwargs):
    return RegularPolygon(n=n, start_angle=PI / 2, **kwargs).scale(radius)


def triangle(size=2, **kwargs):
    return Triangle(**kwargs).scale(size / 2)


def star(n=5, outer_radius=1, inner_radius=0.45, **kwargs):
    pts = [
        polar(outer_radius if i % 2 == 0 else inner_radius,
              PI / 2 + i * PI / n)
        for i in range(2 * n)
    ]
    return Polygon(*pts, **kwargs)


def gear(teeth=12, outer_radius=1, root_radius=0.7, tooth_ratio=0.35, **kwargs):
    pts = []
    for i in range(teeth):
        a = 2 * PI * i / teeth
        da = PI / teeth
        pts += [
            polar(root_radius, a - da),
            polar(root_radius, a - da * tooth_ratio),
            polar(outer_radius, a - da * tooth_ratio),
            polar(outer_radius, a + da * tooth_ratio),
            polar(root_radius, a + da * tooth_ratio),
        ]
    return Polygon(*pts, **kwargs)


def cross(size=1, thickness=0.3, **kwargs):
    h = size / 2
    t = thickness / 2
    pts = [
        [-t, h, 0], [t, h, 0], [t, t, 0],
        [h, t, 0], [h, -t, 0], [t, -t, 0],
        [t, -h, 0], [-t, -h, 0], [-t, -t, 0],
        [-h, -t, 0], [-h, t, 0], [-t, t, 0]
    ]
    return Polygon(*pts, **kwargs)


# ----- Curves -----

def parametric_curve(fn, t_range=(0, 1), **kwargs):
    return ParametricFunction(
        lambda t: np.array(fn(t)),
        t_range=t_range,
        **kwargs
    )


def bezier(points, **kwargs):
    pts = [np.array(p) for p in points]
    return Bezier(*pts, **kwargs)


def quadratic_bezier(p0, p1, p2, **kwargs):
    return parametric_curve(
        lambda t: (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2,
        **kwargs
    )


def cubic_bezier(p0, p1, p2, p3, **kwargs):
    return parametric_curve(
        lambda t:
        (1 - t) ** 3 * p0
        + 3 * (1 - t) ** 2 * t * p1
        + 3 * (1 - t) * t ** 2 * p2
        + t ** 3 * p3,
        **kwargs
    )


def cubic_bezier_path(points, **kwargs):
    pts = list(points)
    curves = VGroup()
    for i in range(0, len(pts) - 3, 3):
        curves.add(cubic_bezier(*pts[i:i + 4], **kwargs))
    return curves


def spiral(turns=3, radius=2, **kwargs):
    return parametric_curve(
        lambda t: polar(radius * t, TAU * turns * t),
        **kwargs
    )


def logarithmic_spiral(a=0.1, b=0.2, turns=4, **kwargs):
    return parametric_curve(
        lambda t: polar(a * np.exp(b * t), t),
        t_range=(0, TAU * turns),
        **kwargs
    )


def wave(amplitude=1, wavelength=2, length=8, **kwargs):
    return parametric_curve(
        lambda x: [x, amplitude * np.sin(TAU * x / wavelength), 0],
        t_range=(-length / 2, length / 2),
        **kwargs
    )


def damped_wave(amplitude=1, decay=0.2, frequency=2, length=8, **kwargs):
    return parametric_curve(
        lambda x: [
            x,
            amplitude * np.exp(-decay * abs(x)) * np.sin(frequency * x),
            0
        ],
        t_range=(-length / 2, length / 2),
        **kwargs
    )


# ----- Mathematical Graphs -----

def function_graph(fn, x_range=(-5, 5), **kwargs):
    return FunctionGraph(
        fn,
        x_range=x_range,
        **kwargs
    )


def parabola(a=1, h=0, k=0, x_range=(-4, 4), **kwargs):
    return function_graph(
        lambda x: a * (x - h) ** 2 + k,
        x_range=x_range,
        **kwargs
    )


def sine_curve(amplitude=1, frequency=1, phase=0, x_range=(-TAU, TAU), **kwargs):
    return function_graph(
        lambda x: amplitude * np.sin(frequency * x + phase),
        x_range=x_range,
        **kwargs
    )


def exponential_curve(base=np.e, x_range=(-3, 3), **kwargs):
    return function_graph(
        lambda x: base ** x,
        x_range=x_range,
        **kwargs
    )


def logarithm_curve(base=np.e, x_range=(0.05, 5), **kwargs):
    return function_graph(
        lambda x: np.log(x) / np.log(base),
        x_range=x_range,
        **kwargs
    )


def circle_path(radius=1, **kwargs):
    return ParametricFunction(
        lambda t: polar(radius, t),
        t_range=(0, TAU),
        **kwargs
    )


def ellipse_path(a=2, b=1, **kwargs):
    return ParametricFunction(
        lambda t: np.array([a * np.cos(t), b * np.sin(t), 0]),
        t_range=(0, TAU),
        **kwargs
    )


# ----- Physics -----

def trajectory(v0=5, angle=PI / 4, gravity=9.8, **kwargs):
    vx = v0 * np.cos(angle)
    vy = v0 * np.sin(angle)
    return parametric_curve(
        lambda t: [vx * t, vy * t - gravity * t ** 2 / 2, 0],
        t_range=(0, 2 * vy / gravity),
        **kwargs
    )


def projectile(v0=5, angle=PI / 4, gravity=9.8, **kwargs):
    return trajectory(v0, angle, gravity, **kwargs)


def circular_motion(radius=2, angular_speed=1, **kwargs):
    return parametric_curve(
        lambda t: polar(radius, angular_speed * t),
        t_range=(0, TAU / angular_speed),
        **kwargs
    )


# ----- Vectors -----

def arrow(a, b, **kwargs):
    return Arrow(a, b, **kwargs)


def double_arrow(a, b, **kwargs):
    return DoubleArrow(a, b, **kwargs)


def vector(v, origin=ORIGIN, **kwargs):
    return Arrow(origin, np.array(origin) + np.array(v), **kwargs)


def vector_field(fn, x_range=(-4, 4, 1), y_range=(-3, 3, 1), scale=0.5, **kwargs):
    arrows = VGroup()
    for x in np.arange(*x_range):
        for y in np.arange(*y_range):
            v = np.array(fn(x, y), dtype=float)
            if np.linalg.norm(v):
                arrows.add(
                    Arrow(
                        [x, y, 0],
                        [x, y, 0] + unit(v) * scale,
                        **kwargs
                    )
                )
    return arrows


def radial_lines(n=12, radius=2, **kwargs):
    return VGroup(*[
        Line(ORIGIN, polar(radius, i * TAU / n), **kwargs)
        for i in range(n)
    ])


# ----- Grids -----

def grid(width=8, height=6, step=1, **kwargs):
    return NumberPlane(
        x_range=[-width / 2, width / 2, step],
        y_range=[-height / 2, height / 2, step],
        **kwargs
    )


def axes(x_range=(-5, 5), y_range=(-4, 4), **kwargs):
    return Axes(
        x_range=x_range,
        y_range=y_range,
        **kwargs
    )


def polar_grid(radius=4, circles=4, radial_count=16, **kwargs):
    g = VGroup()
    for i in range(1, circles + 1):
        g.add(Circle(radius=radius * i / circles, **kwargs))
    g.add(radial_lines(radial_count, radius, **kwargs))
    return g


# ----- Patterns -----

def dotted_line(a, b, dots=20, radius=0.03, **kwargs):
    return VGroup(*[
        Dot(lerp(a, b, i / (dots - 1)), radius=radius, **kwargs)
        for i in range(dots)
    ])


def dotted_circle(radius=2, dots=40, dot_radius=0.03, **kwargs):
    return VGroup(*[
        Dot(polar(radius, TAU * i / dots), radius=dot_radius, **kwargs)
        for i in range(dots)
    ])


def radial_pattern(n=12, radius=2, shape=Dot, **kwargs):
    return VGroup(*[
        shape(polar(radius, i * TAU / n), **kwargs)
        for i in range(n)
    ])


def spiral_dots(turns=3, dots=100, radius=3, **kwargs):
    return VGroup(*[
        Dot(
            polar(
                radius * i / (dots - 1),
                TAU * turns * i / (dots - 1)
            ),
            **kwargs
        )
        for i in range(dots)
    ])


# ----- Effects -----

def impact_ring(radius=0.5, **kwargs):
    return Circle(radius=radius, **kwargs)


def shockwave(radius=0.5, **kwargs):
    return Circle(radius=radius, **kwargs)


def motion_lines(start, direction=RIGHT, count=4, length=0.5, spacing=0.2, **kwargs):
    d = unit(direction)
    p = np.array(start)
    n = np.array([-d[1], d[0], 0])
    return VGroup(*[
        Line(
            p + n * (i - (count - 1) / 2) * spacing,
            p + n * (i - (count - 1) / 2) * spacing + d * length,
            **kwargs
        )
        for i in range(count)
    ])


def sparkle(position=ORIGIN, size=0.3, **kwargs):
    return VGroup(
        Line(position + UP * size, position - UP * size, **kwargs),
        Line(position + RIGHT * size, position - RIGHT * size, **kwargs),
        Line(
            position + (UP + RIGHT) * size * 0.7,
            position - (UP + RIGHT) * size * 0.7,
            **kwargs
        ),
        Line(
            position + (UP - RIGHT) * size * 0.7,
            position - (UP - RIGHT) * size * 0.7,
            **kwargs
        )
    )


def explosion_burst(position=ORIGIN, rays=16, radius=1, **kwargs):
    return VGroup(*[
        Line(
            position + polar(radius * 0.35, a),
            position + polar(radius, a),
            **kwargs
        )
        for a in np.linspace(0, TAU, rays, endpoint=False)
    ])


# ----- Sky -----

def sun(radius=0.6, rays=16, ray_length=0.25, **kwargs):
    body = Circle(radius=radius, **kwargs)
    rays_mob = VGroup(*[
        Line(
            polar(radius + 0.08, i * TAU / rays),
            polar(radius + 0.08 + ray_length, i * TAU / rays),
            **kwargs
        )
        for i in range(rays)
    ])
    return VGroup(body, rays_mob)


def moon(radius=0.55, offset=0.25, **kwargs):
    outer = Circle(radius=radius, **kwargs)
    cut = Circle(radius=radius, **kwargs).shift(RIGHT * offset)
    cut.set_fill(BLACK, 1)
    return VGroup(outer, cut)


def cloud(width=1.8, height=0.7, **kwargs):
    parts = VGroup(
        Ellipse(width=width * 0.65, height=height),
        Circle(radius=height * 0.55).shift(LEFT * width * 0.25 + UP * height * 0.2),
        Circle(radius=height * 0.65).shift(RIGHT * width * 0.15 + UP * height * 0.25),
        Circle(radius=height * 0.45).shift(RIGHT * width * 0.4)
    )
    return parts


def cloud_group(n=5, spacing=2.2, **kwargs):
    return VGroup(*[
        cloud(**kwargs).shift(RIGHT * (i - (n - 1) / 2) * spacing)
        for i in range(n)
    ])


def sky(width=16, height=9, **kwargs):
    return Rectangle(
        width=width,
        height=height,
        **kwargs
    )


# ----- Trees -----

def branch(start, end, width=0.12, **kwargs):
    return Line(start, end, stroke_width=width * 20, **kwargs)


def foliage_cluster(center=ORIGIN, radius=0.5, count=7, spread=0.35, **kwargs):
    return VGroup(*[
        Circle(radius=radius, **kwargs).move_to(
            np.array(center) + np.array([
                np.cos(i * TAU / count) * spread,
                np.sin(i * TAU / count) * spread,
                0
            ])
        )
        for i in range(count)
    ])


def tree(height=4, trunk_width=0.45, crown_width=2.5, **kwargs):
    trunk = Rectangle(
        width=trunk_width,
        height=height * 0.48,
        **kwargs
    ).shift(DOWN * height * 0.26)

    crown = VGroup(
        Circle(radius=crown_width * 0.35, **kwargs).shift(UP * height * 0.05),
        Circle(radius=crown_width * 0.3, **kwargs).shift(
            LEFT * crown_width * 0.28 + UP * height * 0.2
        ),
        Circle(radius=crown_width * 0.3, **kwargs).shift(
            RIGHT * crown_width * 0.28 + UP * height * 0.2
        ),
        Circle(radius=crown_width * 0.28, **kwargs).shift(
            UP * height * 0.35
        )
    )

    return VGroup(trunk, crown)


def pine_tree(height=4, width=2.2, **kwargs):
    trunk = Rectangle(
        width=width * 0.16,
        height=height * 0.3,
        **kwargs
    ).shift(DOWN * height * 0.35)

    layers = VGroup(*[
        Polygon(
            [-w / 2, y - h / 2, 0],
            [w / 2, y - h / 2, 0],
            [0, y + h / 2, 0],
            **kwargs
        )
        for w, h, y in [
            (width, height * 0.42, height * 0.05),
            (width * 0.8, height * 0.35, height * 0.28),
            (width * 0.58, height * 0.3, height * 0.48)
        ]
    ])

    return VGroup(trunk, layers)


def forest(count=10, width=12, min_height=2, max_height=4, seed=7, tree_fn=tree, **kwargs):
    rng = np.random.default_rng(seed)
    trees = VGroup()

    for _ in range(count):
        x = rng.uniform(-width / 2, width / 2)
        h = rng.uniform(min_height, max_height)
        t = tree_fn(height=h, **kwargs)
        t.move_to([x, -2 + h / 2, 0])
        trees.add(t)

    return trees


def forest_layer(count=12, width=14, height_range=(1.5, 3), seed=1, **kwargs):
    return forest(
        count=count,
        width=width,
        min_height=height_range[0],
        max_height=height_range[1],
        seed=seed,
        **kwargs
    )


# ----- Terrain -----

def ground(width=16, height=1, y=-3, **kwargs):
    return Rectangle(
        width=width,
        height=height,
        **kwargs
    ).move_to([0, y, 0])


def hill(width=5, height=2, x=0, y=-2, **kwargs):
    pts = [
        [x - width / 2, y, 0],
        [x - width / 3, y + height * 0.55, 0],
        [x, y + height, 0],
        [x + width / 3, y + height * 0.55, 0],
        [x + width / 2, y, 0]
    ]
    return Polygon(*pts, [x + width / 2, y - 2, 0], [x - width / 2, y - 2, 0], **kwargs)


def mountain(width=4, height=4, x=0, y=-2, snow=False, **kwargs):
    base = Polygon(
        [x - width / 2, y, 0],
        [x, y + height, 0],
        [x + width / 2, y, 0],
        **kwargs
    )

    if not snow:
        return base

    cap = Polygon(
        [x - width * 0.16, y + height * 0.68, 0],
        [x, y + height, 0],
        [x + width * 0.16, y + height * 0.68, 0],
        **kwargs
    )

    return VGroup(base, cap)


def rock(width=0.7, height=0.45, **kwargs):
    return Polygon(
        [-width / 2, -height / 2, 0],
        [-width * 0.3, height / 2, 0],
        [width * 0.2, height * 0.6, 0],
        [width / 2, -height / 2, 0],
        **kwargs
    )


def grass_blade(height=0.3, lean=0.12, **kwargs):
    return Line(
        ORIGIN,
        [lean, height, 0],
        **kwargs
    )


def grass_patch(count=20, width=3, height=0.3, seed=3, **kwargs):
    rng = np.random.default_rng(seed)
    return VGroup(*[
        grass_blade(
            height=rng.uniform(height * 0.7, height * 1.3),
            lean=rng.uniform(-0.15, 0.15),
            **kwargs
        ).shift([rng.uniform(-width / 2, width / 2), 0, 0])
        for _ in range(count)
    ])


# ----- Water -----

def water(width=10, height=2, **kwargs):
    return Rectangle(width=width, height=height, **kwargs)


def water_wave(width=8, amplitude=0.12, wavelength=1.5, **kwargs):
    return wave(
        amplitude=amplitude,
        wavelength=wavelength,
        length=width,
        **kwargs
    )


def water_waves(count=5, width=8, spacing=0.35, **kwargs):
    return VGroup(*[
        water_wave(width=width, **kwargs).shift(DOWN * i * spacing)
        for i in range(count)
    ])


# ----- Structures -----

def ladder(rungs=6, height=3, width=1, **kwargs):
    rails = VGroup(
        Line([-width / 2, 0, 0], [-width / 2, height, 0], **kwargs),
        Line([width / 2, 0, 0], [width / 2, height, 0], **kwargs)
    )
    steps = VGroup(*[
        Line(
            [-width / 2, y, 0],
            [width / 2, y, 0],
            **kwargs
        )
        for y in np.linspace(0, height, rungs)
    ])
    return VGroup(rails, steps)


def fence(posts=6, spacing=0.8, height=1, **kwargs):
    p = VGroup(*[
        Line(
            [i * spacing, 0, 0],
            [i * spacing, height, 0],
            **kwargs
        )
        for i in range(posts)
    ])
    rails = VGroup(
        Line([0, height * 0.7, 0], [(posts - 1) * spacing, height * 0.7, 0], **kwargs),
        Line([0, height * 0.3, 0], [(posts - 1) * spacing, height * 0.3, 0], **kwargs)
    )
    return VGroup(p, rails)


def bridge(width=6, height=1, **kwargs):
    deck = Rectangle(width=width, height=height, **kwargs)
    supports = VGroup(
        Line([-width * 0.35, -height / 2, 0], [-width * 0.35, -height * 2, 0], **kwargs),
        Line([width * 0.35, -height / 2, 0], [width * 0.35, -height * 2, 0], **kwargs)
    )
    return VGroup(deck, supports)


# ----- 3D Geometry -----

def cube(size=2, **kwargs):
    return Cube(side_length=size, **kwargs)


def sphere(radius=1, **kwargs):
    return Sphere(radius=radius, **kwargs)


def cylinder(radius=1, height=2, **kwargs):
    return Cylinder(radius=radius, height=height, **kwargs)


def cone(base_radius=1, height=2, **kwargs):
    return Cone(base_radius=base_radius, height=height, **kwargs)


def torus(major_radius=1.5, minor_radius=0.35, **kwargs):
    return Torus(
        major_radius=major_radius,
        minor_radius=minor_radius,
        **kwargs
    )


# ----- Composition -----

def place(mobject, x=0, y=0, z=0):
    return mobject.move_to([x, y, z])


def center_group(*mobjects):
    group = VGroup(*mobjects)
    group.move_to(ORIGIN)
    return group


def stack(*mobjects, direction=DOWN, buff=0.3):
    return VGroup(*mobjects).arrange(direction, buff=buff)


def distribute(mobjects, start=-5, end=5, axis=0):
    mobjects = list(mobjects)
    values = np.linspace(start, end, len(mobjects))
    for m, value in zip(mobjects, values):
        pos = m.get_center()
        pos[axis] = value
        m.move_to(pos)
    return VGroup(*mobjects)


def scatter(count=20, x_range=(-5, 5), y_range=(-3, 3), seed=0, **kwargs):
    rng = np.random.default_rng(seed)
    return VGroup(*[
        Dot(
            [
                rng.uniform(*x_range),
                rng.uniform(*y_range),
                0
            ],
            **kwargs
        )
        for _ in range(count)
    ])


def random_points(count=20, x_range=(-5, 5), y_range=(-3, 3), seed=0):
    rng = np.random.default_rng(seed)
    return np.array([
        [
            rng.uniform(*x_range),
            rng.uniform(*y_range),
            0
        ]
        for _ in range(count)
    ])


# ----- Environment -----

def landscape(
    ground_y=-3,
    mountains=3,
    trees=8,
    width=14,
    seed=5,
    **kwargs
):
    rng = np.random.default_rng(seed)

    far = VGroup(*[
        mountain(
            width=rng.uniform(3, 5),
            height=rng.uniform(2.5, 4.5),
            x=rng.uniform(-width / 2, width / 2),
            y=ground_y + 0.2,
            **kwargs
        )
        for _ in range(mountains)
    ])

    trees_mob = forest(
        count=trees,
        width=width,
        min_height=1.8,
        max_height=3.8,
        seed=seed + 1,
        **kwargs
    )

    floor = ground(width=width + 2, y=ground_y, **kwargs)

    return VGroup(far, trees_mob, floor)


def forest_scene(
    width=14,
    ground_y=-3,
    tree_count=12,
    seed=10,
    **kwargs
):
    return VGroup(
        ground(width=width + 2, y=ground_y, **kwargs),
        forest(
            count=tree_count,
            width=width,
            min_height=2,
            max_height=4,
            seed=seed,
            **kwargs
        )
    )