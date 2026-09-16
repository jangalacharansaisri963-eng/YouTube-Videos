from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageEnhance
import math
import random


# ----- Core -----

def canvas(size=(1920, 1080), background=(0, 0, 0, 0)):
    return Image.new("RGBA", size, background)


def draw(image):
    return ImageDraw.Draw(image, "RGBA")


def rgba(color, alpha=255):
    if len(color) == 4:
        return color
    return (*color, alpha)


def font(size, path=None):
    if path:
        return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def save(image, path, quality=95):
    image.save(path, quality=quality)
    return image


def resize(image, size):
    return image.resize(size, Image.Resampling.LANCZOS)


def scale(image, factor):
    return resize(image, tuple(round(v * factor) for v in image.size))


def crop(image, box):
    return image.crop(box)


def copy(image):
    return image.copy()


# ----- Coordinates -----

def polar(cx, cy, radius, angle):
    return (
        cx + radius * math.cos(angle),
        cy + radius * math.sin(angle)
    )


def midpoint(a, b):
    return (
        (a[0] + b[0]) / 2,
        (a[1] + b[1]) / 2
    )


def distance(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def lerp(a, b, t):
    return (
        a[0] + (b[0] - a[0]) * t,
        a[1] + (b[1] - a[1]) * t
    )


def polygon_points(cx, cy, radius, sides, rotation=-math.pi / 2):
    return [
        polar(cx, cy, radius, rotation + i * 2 * math.pi / sides)
        for i in range(sides)
    ]


# ----- Text -----

def text_box(image, text, xy, size=48, fill=(255, 255, 255, 255),
             font_path=None, anchor="la", stroke=0, stroke_fill=(0, 0, 0, 255)):
    d = draw(image)
    f = font(size, font_path)
    d.text(
        xy,
        text,
        font=f,
        fill=fill,
        anchor=anchor,
        stroke_width=stroke,
        stroke_fill=stroke_fill
    )
    return image


def centered_text(image, text, center, size=48, **kwargs):
    return text_box(
        image,
        text,
        center,
        size=size,
        anchor="mm",
        **kwargs
    )


def multiline_text(image, text, xy, size=42, spacing=8, **kwargs):
    d = draw(image)
    d.multiline_text(
        xy,
        text,
        font=font(size, kwargs.pop("font_path", None)),
        spacing=spacing,
        **kwargs
    )
    return image


def text_size(text, size=48, font_path=None):
    f = font(size, font_path)
    return f.getbbox(text)


def fit_text(text, max_width, start_size=100, min_size=10, font_path=None):
    size = start_size
    while size > min_size:
        box = text_size(text, size, font_path)
        if box[2] - box[0] <= max_width:
            return font(size, font_path)
        size -= 2
    return font(min_size, font_path)


# ----- Basic Shapes -----

def rectangle(image, box, fill=None, outline=None, width=1, radius=0):
    d = draw(image)
    if radius:
        d.rounded_rectangle(
            box,
            radius=radius,
            fill=fill,
            outline=outline,
            width=width
        )
    else:
        d.rectangle(
            box,
            fill=fill,
            outline=outline,
            width=width
        )
    return image


def ellipse(image, box, fill=None, outline=None, width=1):
    draw(image).ellipse(
        box,
        fill=fill,
        outline=outline,
        width=width
    )
    return image


def circle(image, center, radius, fill=None, outline=None, width=1):
    x, y = center
    return ellipse(
        image,
        (x - radius, y - radius, x + radius, y + radius),
        fill,
        outline,
        width
    )


def line(image, points, fill=(255, 255, 255, 255), width=4, joint="curve"):
    draw(image).line(points, fill=fill, width=width, joint=joint)
    return image


def polygon(image, points, fill=None, outline=None, width=1):
    draw(image).polygon(points, fill=fill)
    if outline:
        draw(image).line(
            points + [points[0]],
            fill=outline,
            width=width,
            joint="curve"
        )
    return image


def arc(image, box, start, end, fill=(255, 255, 255, 255), width=4):
    draw(image).arc(box, start, end, fill=fill, width=width)
    return image


def pie(image, box, start, end, fill):
    draw(image).pieslice(box, start, end, fill=fill)
    return image


def star(image, center, outer, inner, points=5, fill=None, outline=None, width=1):
    pts = []
    for i in range(points * 2):
        r = outer if i % 2 == 0 else inner
        pts.append(
            polar(
                center[0],
                center[1],
                r,
                -math.pi / 2 + i * math.pi / points
            )
        )
    return polygon(image, pts, fill, outline, width)


def gear(image, center, outer, inner, teeth=12, fill=None, outline=None, width=1):
    pts = []
    step = 2 * math.pi / teeth

    for i in range(teeth):
        a = i * step
        for offset, radius in (
            (-0.5, inner),
            (-0.25, outer),
            (0.25, outer),
            (0.5, inner)
        ):
            pts.append(
                polar(
                    center[0],
                    center[1],
                    radius,
                    a + offset * step
                )
            )

    return polygon(image, pts, fill, outline, width)


# ----- Mathematical Diagrams -----

def axes(image, origin, x_length=600, y_length=400,
         step=50, fill=(180, 180, 180, 255), width=2):
    ox, oy = origin
    d = draw(image)

    d.line((ox, oy, ox + x_length, oy), fill=fill, width=width)
    d.line((ox, oy, ox, oy - y_length), fill=fill, width=width)

    for x in range(0, x_length + 1, step):
        d.line((ox + x, oy - 6, ox + x, oy + 6), fill=fill, width=width)

    for y in range(0, y_length + 1, step):
        d.line((ox - 6, oy - y, ox + 6, oy - y), fill=fill, width=width)

    return image


def graph(image, fn, origin, x_range, scale_x=50, scale_y=50,
          fill=(80, 200, 255, 255), width=5, samples=1000):
    ox, oy = origin
    x0, x1 = x_range
    pts = []

    for i in range(samples + 1):
        x = x0 + (x1 - x0) * i / samples
        try:
            y = fn(x)
            if math.isfinite(y):
                pts.append((ox + x * scale_x, oy - y * scale_y))
        except (ValueError, OverflowError):
            if len(pts) > 1:
                line(image, pts, fill, width)
            pts = []

    if len(pts) > 1:
        line(image, pts, fill, width)

    return image


def sine_wave(image, center, amplitude=50, wavelength=200,
              length=800, fill=(255, 255, 255, 255), width=4):
    cx, cy = center
    pts = [
        (
            cx + x,
            cy + amplitude * math.sin(2 * math.pi * x / wavelength)
        )
        for x in range(length + 1)
    ]
    return line(image, pts, fill, width)


def parabola(image, origin, a=0.01, x_range=(-300, 300),
             fill=(255, 200, 80, 255), width=4):
    ox, oy = origin
    pts = [
        (ox + x, oy - a * x * x)
        for x in range(x_range[0], x_range[1] + 1)
    ]
    return line(image, pts, fill, width)


def circle_diagram(image, center, radius, subdivisions=0,
                   fill=None, outline=(255, 255, 255, 255), width=4):
    circle(image, center, radius, fill, outline, width)

    if subdivisions:
        for i in range(subdivisions):
            a = i * math.pi * 2 / subdivisions
            line(
                image,
                [center, polar(*center, radius, a)],
                outline,
                max(1, width // 2)
            )

    return image


# ----- Geometry Diagrams -----

def triangle_diagram(image, a, b, c, labels=None,
                     fill=None, outline=(255, 255, 255, 255), width=4):
    polygon(image, [a, b, c], fill, outline, width)

    if labels:
        for p, label in zip((a, b, c), labels):
            centered_text(image, label, p, 28)

    return image


def angle_marker(image, vertex, a, b, radius=50,
                 fill=(255, 220, 80, 255), width=4):
    va = math.atan2(a[1] - vertex[1], a[0] - vertex[0])
    vb = math.atan2(b[1] - vertex[1], b[0] - vertex[0])

    start = math.degrees(va)
    end = math.degrees(vb)

    x, y = vertex
    return arc(
        image,
        (x - radius, y - radius, x + radius, y + radius),
        start,
        end,
        fill,
        width
    )


def vector(image, start, end, fill=(255, 255, 255, 255), width=5, head=20):
    line(image, [start, end], fill, width)

    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    left = polar(end[0], end[1], head, angle + math.pi - 0.45)
    right = polar(end[0], end[1], head, angle + math.pi + 0.45)

    polygon(image, [end, left, right], fill)
    return image


def coordinate_point(image, origin, x, y, scale=50,
                     radius=8, fill=(255, 100, 100, 255)):
    p = (origin[0] + x * scale, origin[1] - y * scale)
    circle(image, p, radius, fill)
    return p


# ----- Flowcharts -----

def flow_box(image, box, text, fill=(35, 35, 45, 255),
             outline=(220, 220, 220, 255), radius=20,
             text_fill=(255, 255, 255, 255), text_size_value=30):
    rectangle(image, box, fill, outline, 3, radius)

    x1, y1, x2, y2 = box
    centered_text(
        image,
        text,
        ((x1 + x2) / 2, (y1 + y2) / 2),
        text_size_value,
        fill=text_fill
    )

    return image


def flow_arrow(image, start, end, **kwargs):
    return vector(image, start, end, **kwargs)


def decision_diamond(image, center, width, height, text="",
                     fill=(45, 45, 55, 255),
                     outline=(255, 255, 255, 255)):
    x, y = center
    pts = [
        (x, y - height / 2),
        (x + width / 2, y),
        (x, y + height / 2),
        (x - width / 2, y)
    ]

    polygon(image, pts, fill, outline, 3)

    if text:
        centered_text(image, text, center, 26)

    return image


# ----- Science Diagrams -----

def atom(image, center, radius=100, electrons=6,
         nucleus_fill=(220, 80, 80, 255),
         orbit_fill=(120, 180, 255, 255),
         electron_fill=(255, 220, 80, 255)):
    circle(image, center, radius * 0.25, nucleus_fill)

    for i in range(3):
        box = (
            center[0] - radius,
            center[1] - radius * 0.55,
            center[0] + radius,
            center[1] + radius * 0.55
        )
        arc(
            image,
            box,
            i * 60,
            180 + i * 60,
            orbit_fill,
            3
        )

    for i in range(electrons):
        angle = i * 2 * math.pi / electrons
        p = polar(center[0], center[1], radius, angle)
        circle(image, p, 10, electron_fill)

    return image


def molecule(image, atoms, bonds, atom_radius=30,
             atom_fill=(100, 180, 255, 255),
             bond_fill=(220, 220, 220, 255)):
    for a, b in bonds:
        line(image, [atoms[a], atoms[b]], bond_fill, 12)

    for p in atoms:
        circle(image, p, atom_radius, atom_fill)

    return image


def force_diagram(image, object_box, forces):
    rectangle(image, object_box, (60, 60, 70, 255))

    cx = (object_box[0] + object_box[2]) / 2
    cy = (object_box[1] + object_box[3]) / 2

    for direction, magnitude, label in forces:
        d = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0)
        }[direction]

        end = (
            cx + d[0] * magnitude,
            cy + d[1] * magnitude
        )

        vector(image, (cx, cy), end, width=5)
        centered_text(
            image,
            label,
            (
                end[0] + d[0] * 30,
                end[1] + d[1] * 30
            ),
            26
        )

    return image


# ----- Maps and Terrain -----

def map_grid(image, box, spacing=80, fill=(80, 100, 110, 255), width=2):
    x1, y1, x2, y2 = box
    d = draw(image)

    for x in range(int(x1), int(x2) + 1, spacing):
        d.line((x, y1, x, y2), fill=fill, width=width)

    for y in range(int(y1), int(y2) + 1, spacing):
        d.line((x1, y, x2, y), fill=fill, width=width)

    return image


def contour_lines(image, center, radii, fill=(255, 255, 255, 100), width=3):
    for r in radii:
        ellipse(
            image,
            (
                center[0] - r,
                center[1] - r * 0.7,
                center[0] + r,
                center[1] + r * 0.7
            ),
            outline=fill,
            width=width
        )
    return image


def mountain(image, base, width, height,
             fill=(90, 100, 110, 255),
             snow=False):
    x, y = base
    pts = [
        (x - width / 2, y),
        (x - width * 0.18, y - height * 0.65),
        (x, y - height),
        (x + width * 0.18, y - height * 0.65),
        (x + width / 2, y)
    ]
    polygon(image, pts, fill)

    if snow:
        polygon(
            image,
            [
                (x - width * 0.18, y - height * 0.65),
                (x, y - height),
                (x + width * 0.18, y - height * 0.65),
                (x + width * 0.08, y - height * 0.72),
                (x, y - height * 0.58),
                (x - width * 0.08, y - height * 0.72)
            ],
            (235, 240, 245, 255)
        )

    return image


def tree(image, base, height=300, width=180,
         trunk_fill=(100, 60, 35, 255),
         leaf_fill=(40, 130, 60, 255)):
    x, y = base

    rectangle(
        image,
        (
            x - width * 0.09,
            y - height * 0.4,
            x + width * 0.09,
            y
        ),
        trunk_fill
    )

    for dx, dy, r in (
        (-0.25, -0.55, 0.28),
        (0, -0.7, 0.34),
        (0.25, -0.55, 0.28),
        (0, -0.48, 0.3)
    ):
        circle(
            image,
            (x + dx * width, y + dy * height),
            r * width,
            leaf_fill
        )

    return image


def forest(image, base_y, count=15, spacing=140,
           seed=1, height_range=(180, 360)):
    rng = random.Random(seed)
    w, _ = image.size

    for i in range(count):
        x = i * spacing + rng.randint(-30, 30)
        h = rng.randint(*height_range)
        tree(image, (x, base_y), h, h * 0.6)

    return image


# ----- Technical Diagrams -----

def dimension_line(image, a, b, label=None,
                   fill=(255, 220, 80, 255), width=3, arrow_size=15):
    vector(image, a, b, fill, width, arrow_size)
    vector(image, b, a, fill, width, arrow_size)

    if label:
        centered_text(
            image,
            label,
            midpoint(a, b),
            28,
            fill=fill
        )

    return image


def ruler(image, start, end, ticks=10,
          fill=(230, 230, 230, 255), width=3):
    line(image, [start, end], fill, width)

    for i in range(ticks + 1):
        t = i / ticks
        p = lerp(start, end, t)
        circle(image, p, 3, fill)

    return image


def blueprint(image, box, spacing=50,
              grid_fill=(40, 100, 160, 90),
              border_fill=(80, 180, 255, 255)):
    map_grid(image, box, spacing, grid_fill, 1)
    rectangle(image, box, outline=border_fill, width=4)
    return image


# ----- Patterns -----

def dotted_pattern(image, box, spacing=30, radius=3,
                   fill=(255, 255, 255, 180)):
    x1, y1, x2, y2 = box

    for y in range(int(y1), int(y2), spacing):
        for x in range(int(x1), int(x2), spacing):
            circle(image, (x, y), radius, fill)

    return image


def checkerboard(image, box, cell=50,
                 a=(30, 30, 30, 255),
                 b=(220, 220, 220, 255)):
    x1, y1, x2, y2 = box

    for row, y in enumerate(range(int(y1), int(y2), cell)):
        for col, x in enumerate(range(int(x1), int(x2), cell)):
            rectangle(
                image,
                (x, y, x + cell, y + cell),
                a if (row + col) % 2 == 0 else b
            )

    return image


def radial_pattern(image, center, radius, count=32,
                   fill=(255, 255, 255, 180), width=3):
    for i in range(count):
        a = i * 2 * math.pi / count
        line(
            image,
            [
                polar(*center, radius * 0.15, a),
                polar(*center, radius, a)
            ],
            fill,
            width
        )
    return image


# ----- Lighting -----

def glow(image, center, radius=150,
         color=(255, 255, 255, 100), strength=5):
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    d = draw(layer)

    for i in range(strength, 0, -1):
        r = radius * i / strength
        alpha = int(color[3] * (1 - i / (strength + 1)) ** 2)

        circle(
            layer,
            center,
            r,
            rgba(color, alpha)
        )

    layer = layer.filter(ImageFilter.GaussianBlur(radius / 8))
    image.alpha_composite(layer)
    return image


def vignette(image, strength=0.65):
    w, h = image.size
    layer = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(layer)

    d.ellipse(
        (
            -w * 0.15,
            -h * 0.15,
            w * 1.15,
            h * 1.15
        ),
        fill=int(255 * strength)
    )

    layer = ImageChops.invert(layer)
    layer = layer.filter(ImageFilter.GaussianBlur(min(w, h) * 0.15))

    dark = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dark.putalpha(layer)
    image.alpha_composite(dark)
    return image


def shadow(image, box, offset=(15, 15), blur=20,
           alpha=120):
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shifted = (
        box[0] + offset[0],
        box[1] + offset[1],
        box[2] + offset[0],
        box[3] + offset[1]
    )

    rectangle(layer, shifted, (0, 0, 0, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    image.alpha_composite(layer)
    return image


# ----- Particles -----

def particles(image, center, count=100, radius=300,
              seed=0, size=(2, 8),
              fill=(255, 255, 255, 180)):
    rng = random.Random(seed)

    for _ in range(count):
        angle = rng.random() * 2 * math.pi
        r = radius * math.sqrt(rng.random())
        p = polar(center[0], center[1], r, angle)
        s = rng.randint(*size)
        circle(image, p, s, fill)

    return image


def sparks(image, center, count=30, radius=150,
           seed=0, fill=(255, 220, 80, 255)):
    rng = random.Random(seed)

    for _ in range(count):
        angle = rng.random() * 2 * math.pi
        r = rng.uniform(radius * 0.3, radius)
        p = polar(center[0], center[1], r, angle)
        line(
            image,
            [
                p,
                polar(p[0], p[1], rng.uniform(5, 15), angle)
            ],
            fill,
            rng.randint(2, 5)
        )

    return image


# ----- Texture -----

def noise(image, amount=25, seed=0):
    rng = random.Random(seed)
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    px = overlay.load()

    for y in range(0, image.height, 2):
        for x in range(0, image.width, 2):
            a = rng.randint(0, amount)
            px[x, y] = (255, 255, 255, a)

    image.alpha_composite(overlay)
    return image


def paper_texture(image, strength=20, seed=0):
    noise(image, strength, seed)
    return image.filter(ImageFilter.GaussianBlur(0.25))


# ----- Gradients -----

def vertical_gradient(size, top, bottom):
    w, h = size
    image = Image.new("RGBA", size)

    px = image.load()

    for y in range(h):
        t = y / max(1, h - 1)
        c = tuple(
            round(top[i] * (1 - t) + bottom[i] * t)
            for i in range(4)
        )

        for x in range(w):
            px[x, y] = c

    return image


def horizontal_gradient(size, left, right):
    w, h = size
    image = Image.new("RGBA", size)

    px = image.load()

    for x in range(w):
        t = x / max(1, w - 1)
        c = tuple(
            round(left[i] * (1 - t) + right[i] * t)
            for i in range(4)
        )

        for y in range(h):
            px[x, y] = c

    return image


# ----- Compositing -----

def layer(base, overlay, position=(0, 0)):
    base.alpha_composite(overlay, position)
    return base


def transparent_layer(size):
    return Image.new("RGBA", size, (0, 0, 0, 0))


def tint(image, color, strength=0.25):
    overlay = Image.new("RGBA", image.size, rgba(color, int(255 * strength)))
    image.alpha_composite(overlay)
    return image


def brightness(image, value=1.0):
    return ImageEnhance.Brightness(image).enhance(value)


def contrast(image, value=1.0):
    return ImageEnhance.Contrast(image).enhance(value)


def sharpen(image, amount=1.5):
    return ImageEnhance.Sharpness(image).enhance(amount)


# ----- Reusable Scenes -----

def sunset(image, horizon=None,
           sky_top=(25, 35, 100, 255),
           sky_bottom=(255, 120, 60, 255)):
    horizon = horizon or image.height * 0.65

    top = vertical_gradient(
        (image.width, int(horizon)),
        sky_top,
        sky_bottom
    )

    image.alpha_composite(top)

    sun_pos = (image.width * 0.75, horizon * 0.75)
    glow(image, sun_pos, 180, (255, 180, 70, 100))
    circle(image, sun_pos, 70, (255, 190, 80, 255))

    return image


def night_sky(image, stars=150, seed=4):
    image.paste((8, 12, 30, 255), (0, 0, image.width, image.height))
    particles(
        image,
        (image.width / 2, image.height / 2),
        stars,
        max(image.width, image.height),
        seed,
        (1, 3),
        (255, 255, 255, 200)
    )

    moon_pos = (image.width * 0.8, image.height * 0.2)
    circle(image, moon_pos, 65, (240, 240, 220, 255))
    circle(image, (moon_pos[0] + 22, moon_pos[1] - 10), 65, (8, 12, 30, 255))

    return image


def forest_background(image, ground_y=None, seed=2):
    ground_y = ground_y or int(image.height * 0.78)

    vertical_gradient(
        image.size,
        (100, 180, 255, 255),
        (220, 240, 255, 255)
    )

    forest(
        image,
        ground_y,
        count=max(8, image.width // 130),
        spacing=130,
        seed=seed,
        height_range=(180, 350)
    )

    rectangle(
        image,
        (0, ground_y, image.width, image.height),
        (55, 110, 55, 255)
    )

    return image


# ----- Diagram Panels -----

def panel(image, box, title=None,
          fill=(20, 25, 35, 235),
          outline=(100, 120, 150, 255)):
    rectangle(image, box, fill, outline, 3, 20)

    if title:
        x1, y1, x2, _ = box
        text_box(
            image,
            title,
            (x1 + 25, y1 + 20),
            32,
            fill=(255, 255, 255, 255)
        )

    return image


def legend(image, items, position=(40, 40), spacing=45, size=24):
    x, y = position

    for i, (label, color) in enumerate(items):
        yy = y + i * spacing
        circle(image, (x, yy), 10, color)
        text_box(
            image,
            label,
            (x + 25, yy),
            size,
            anchor="lm"
        )

    return image


# ----- Infographics -----

def progress_bar(image, box, value, maximum=100,
                 fill=(80, 190, 255, 255),
                 background=(45, 50, 60, 255)):
    x1, y1, x2, y2 = box
    rectangle(image, box, background, radius=(y2 - y1) / 2)

    ratio = max(0, min(1, value / maximum))
    rectangle(
        image,
        (x1, y1, x1 + (x2 - x1) * ratio, y2),
        fill,
        radius=(y2 - y1) / 2
    )

    return image


def pie_chart(image, center, radius, values,
              colors, start=-math.pi / 2):
    total = sum(values)
    angle = start

    for value, color in zip(values, colors):
        sweep = 2 * math.pi * value / total

        pie(
            image,
            (
                center[0] - radius,
                center[1] - radius,
                center[0] + radius,
                center[1] + radius
            ),
            math.degrees(angle),
            math.degrees(angle + sweep),
            color
        )

        angle += sweep

    return image


def bar_chart(image, origin, values, bar_width=60,
              spacing=25, scale=5,
              fill=(80, 180, 255, 255)):
    ox, oy = origin

    for i, value in enumerate(values):
        x1 = ox + i * (bar_width + spacing)
        x2 = x1 + bar_width
        y2 = oy - value * scale

        rectangle(
            image,
            (x1, y2, x2, oy),
            fill
        )

    return image


# ----- High-Level Diagram Builders -----

def math_card(size=(1200, 700), title="Mathematics"):
    image = canvas(size, (15, 18, 28, 255))
    panel(
        image,
        (40, 40, size[0] - 40, size[1] - 40),
        title
    )
    return image


def science_card(size=(1200, 700), title="Science"):
    image = canvas(size, (12, 20, 28, 255))
    panel(
        image,
        (40, 40, size[0] - 40, size[1] - 40),
        title
    )
    return image


def infographic(size=(1920, 1080), title=""):
    image = canvas(size, (12, 15, 22, 255))

    if title:
        centered_text(
            image,
            title,
            (size[0] / 2, 80),
            58,
            fill=(255, 255, 255, 255)
        )

    return image

# ----- Reusable Diagrams -----

def number_line(image, start, end, y, step=1, scale=60,
                origin_x=None, fill=(230, 230, 230, 255),
                width=3, tick=12, label_size=22):
    if end < start or step <= 0:
        return image

    ox = origin_x if origin_x is not None else 0
    x1 = ox + start * scale
    x2 = ox + end * scale

    line(image, [(x1, y), (x2, y)], fill, width)

    for n in range(start, end + 1, step):
        x = ox + n * scale
        line(image, [(x, y - tick), (x, y + tick)], fill, width)
        centered_text(image, str(n), (x, y + tick + 20),
                      label_size, fill=fill)

    vector(image, (x1 + 10, y), (x1, y), fill, width, 12)
    vector(image, (x2 - 10, y), (x2, y), fill, width, 12)

    return image


def fraction_bar(image, box, numerator, denominator,
                 fill=(80, 180, 255, 255),
                 background=(50, 55, 65, 255),
                 outline=(220, 220, 230, 255),
                 width=3, radius=8):
    x1, y1, x2, y2 = box

    if denominator <= 0:
        raise ValueError("denominator must be positive")

    numerator = max(0, min(numerator, denominator))
    part = (x2 - x1) / denominator

    rectangle(image, box, background, outline, width, radius)

    for i in range(1, denominator):
        x = x1 + i * part
        line(image, [(x, y1), (x, y2)], outline, 2)

    filled = x1 + numerator * part

    if numerator:
        rectangle(
            image,
            (x1, y1, filled, y2),
            fill
        )

    centered_text(
        image,
        f"{numerator}/{denominator}",
        ((x1 + x2) / 2, (y1 + y2) / 2),
        28,
        fill=(255, 255, 255, 255)
    )

    return image


def multiplication_grid(image, rows, cols, box,
                        fill=(70, 160, 230, 255),
                        outline=(220, 220, 220, 255),
                        labels=True, label_size=20):
    if rows <= 0 or cols <= 0:
        raise ValueError("rows and cols must be positive")

    x1, y1, x2, y2 = box
    cw = (x2 - x1) / cols
    ch = (y2 - y1) / rows

    for r in range(rows):
        for c in range(cols):
            b = (
                x1 + c * cw,
                y1 + r * ch,
                x1 + (c + 1) * cw,
                y1 + (r + 1) * ch
            )

            rectangle(image, b, fill, outline, 2)

            if labels:
                centered_text(
                    image,
                    str((r + 1) * (c + 1)),
                    ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2),
                    label_size,
                    fill=(255, 255, 255, 255)
                )

    return image


def venn_diagram(image, centers, radii, labels=None,
                 fills=None, outline=(255, 255, 255, 255),
                 width=4, label_size=30):
    if len(centers) != len(radii):
        raise ValueError("centers and radii must have equal lengths")

    for i, (center, radius) in enumerate(zip(centers, radii)):
        color = (
            fills[i] if fills and i < len(fills)
            else (80, 160, 240, 100)
        )

        circle(image, center, radius, color, outline, width)

        if labels and i < len(labels):
            label_pos = (
                center[0],
                center[1] - radius * 0.72
            )
            centered_text(
                image,
                str(labels[i]),
                label_pos,
                label_size
            )

    return image


def set_diagram(image, items, box, title=None,
                fill=(35, 40, 50, 255),
                outline=(150, 160, 180, 255)):
    x1, y1, x2, y2 = box
    panel(image, box, title, fill)

    if outline:
        rectangle(image, box, None, outline, 2)

    content = "{ " + ", ".join(map(str, items)) + " }"

    centered_text(
        image,
        content,
        ((x1 + x2) / 2, (y1 + y2) / 2),
        28,
        fill=(240, 240, 245, 255)
    )

    return image


def matrix(image, values, origin, cell=70,
           fill=(35, 40, 50, 255),
           outline=(180, 190, 210, 255),
           label_size=26):
    if not values or not any(values):
        raise ValueError("matrix cannot be empty")

    rows = len(values)
    cols = max(len(row) for row in values)

    x, y = origin

    for r, row in enumerate(values):
        for c, value in enumerate(row):
            b = (
                x + c * cell,
                y + r * cell,
                x + (c + 1) * cell,
                y + (r + 1) * cell
            )

            rectangle(image, b, fill, outline, 2)

            centered_text(
                image,
                str(value),
                (
                    (b[0] + b[2]) / 2,
                    (b[1] + b[3]) / 2
                ),
                label_size
            )

    return image


def binary_tree(image, root, levels=3, dx=180, dy=100,
                node_radius=28, labels=None,
                fill=(60, 130, 220, 255),
                outline=(240, 240, 240, 255)):
    if levels < 1:
        return image

    nodes = [[root]]
    current_dx = dx

    for _ in range(1, levels):
        previous = nodes[-1]
        current = []

        for x, y in previous:
            current.extend((
                (x - current_dx / 2, y + dy),
                (x + current_dx / 2, y + dy)
            ))

        nodes.append(current)
        current_dx *= 0.55

    for parents, children in zip(nodes, nodes[1:]):
        for i, parent in enumerate(parents):
            a = 2 * i
            if a < len(children):
                line(image, [parent, children[a]], outline, 3)
            if a + 1 < len(children):
                line(image, [parent, children[a + 1]], outline, 3)

    index = 0

    for level in nodes:
        for p in level:
            circle(image, p, node_radius, fill, outline, 3)

            if labels and index < len(labels):
                centered_text(image, str(labels[index]), p, 20)

            index += 1

    return image


def circuit_gate(image, box, gate="AND",
                 fill=(40, 45, 55, 255),
                 outline=(100, 200, 255, 255),
                 width=3, label=True):
    x1, y1, x2, y2 = box
    gate = gate.upper()
    cy = (y1 + y2) / 2
    h = y2 - y1
    w = x2 - x1

    if gate in ("AND", "NAND"):
        r = h / 2
        pts = [
            (x1, y1),
            (x1 + w * 0.45, y1),
            (x1 + w * 0.72, y1 + h * 0.08),
            (x2, cy),
            (x1 + w * 0.72, y2 - h * 0.08),
            (x1 + w * 0.45, y2),
            (x1, y2)
        ]

        polygon(image, pts, fill, outline, width)

    elif gate in ("OR", "NOR", "XOR", "XNOR"):
        pts = [
            (x1, y1),
            (x1 + w * 0.28, cy),
            (x1, y2),
            (x1 + w * 0.52, y2 - h * 0.08),
            (x2, cy),
            (x1 + w * 0.52, y1 + h * 0.08)
        ]

        polygon(image, pts, fill, outline, width)

        if gate in ("XOR", "XNOR"):
            offset = w * 0.10
            line(
                image,
                [
                    (x1 + offset, y1 + h * 0.08),
                    (x1 + offset + w * 0.28, cy),
                    (x1 + offset, y2 - h * 0.08)
                ],
                outline,
                width
            )

    elif gate == "NOT":
        pts = [
            (x1, y1),
            (x2 - 20, cy),
            (x1, y2)
        ]
        polygon(image, pts, fill, outline, width)
        circle(image, (x2 - 10, cy), 10, fill, outline, width)

    else:
        raise ValueError(
            "gate must be AND, OR, XOR, NOT, NAND, NOR or XNOR"
        )

    if gate in ("NAND", "NOR", "XNOR"):
        circle(image, (x2 + 10, cy), 10, fill, outline, width)

    if label:
        centered_text(
            image,
            gate,
            ((x1 + x2) / 2, cy),
            20
        )

    return image


def circuit_wire(image, points, **kwargs):
    if len(points) < 2:
        raise ValueError("wire needs at least two points")
    return line(image, points, **kwargs)


def bar_chart_labeled(image, values, labels, origin,
                      width=65, spacing=30, scale=5,
                      fill=(80, 180, 255, 255),
                      baseline=True):
    if len(values) != len(labels):
        raise ValueError("values and labels must have equal lengths")

    x, y = origin

    if baseline:
        total = len(values) * width + max(0, len(values) - 1) * spacing
        line(image, [(x, y), (x + total, y)], width=3)

    for i, (value, label) in enumerate(zip(values, labels)):
        x1 = x + i * (width + spacing)
        x2 = x1 + width
        y1 = y - value * scale

        rectangle(image, (x1, y1, x2, y), fill)

        centered_text(
            image,
            str(value),
            ((x1 + x2) / 2, y1 - 22),
            22
        )

        centered_text(
            image,
            str(label),
            ((x1 + x2) / 2, y + 25),
            20
        )

    return image


def line_chart(image, values, origin,
               spacing=80, scale=5,
               fill=(80, 200, 255, 255), width=5,
               show_values=True):
    if not values:
        return image

    pts = [
        (
            origin[0] + i * spacing,
            origin[1] - value * scale
        )
        for i, value in enumerate(values)
    ]

    line(image, pts, fill, width)

    for value, p in zip(values, pts):
        circle(image, p, 7, fill)

        if show_values:
            centered_text(
                image,
                str(value),
                (p[0], p[1] - 24),
                20
            )

    return image


def histogram(image, values, origin,
              bin_width=60, spacing=5, scale=5,
              fill=(100, 170, 240, 255),
              outline=(230, 230, 240, 255)):
    x, y = origin

    for i, value in enumerate(values):
        x1 = x + i * (bin_width + spacing)
        x2 = x1 + bin_width
        y1 = y - value * scale

        rectangle(
            image,
            (x1, y1, x2, y),
            fill,
            outline,
            2
        )

    line(image, [(x, y), (x + len(values) *
         (bin_width + spacing), y)], outline, 3)

    return image


def thermometer(image, center, height=350,
                value=50, minimum=0, maximum=100,
                tube_w=30, bulb=55,
                fill=(230, 70, 70, 255),
                background=(220, 225, 230, 255)):
    if maximum <= minimum:
        raise ValueError("maximum must be greater than minimum")

    x, y = center
    top = y - height / 2
    bottom = y + height / 2

    rectangle(
        image,
        (x - tube_w / 2, top, x + tube_w / 2, bottom),
        background,
        (50, 50, 60, 255),
        3,
        tube_w / 2
    )

    circle(
        image,
        (x, bottom),
        bulb,
        fill
    )

    ratio = max(0, min(
        1,
        (value - minimum) / (maximum - minimum)
    ))

    liquid_bottom = bottom
    liquid_top = bottom - ratio * height

    line(
        image,
        [(x, liquid_bottom), (x, liquid_top)],
        fill,
        max(4, tube_w - 8)
    )

    return image


def speedometer(image, center, radius=150,
                value=50, maximum=100,
                fill=(220, 220, 230, 255),
                needle=(255, 100, 80, 255)):
    if maximum <= 0:
        raise ValueError("maximum must be positive")

    x, y = center

    start = 135
    sweep = 270

    arc(
        image,
        (x - radius, y - radius,
         x + radius, y + radius),
        start,
        start + sweep,
        fill,
        8
    )

    for i in range(11):
        ratio = i / 10
        angle = math.radians(start + sweep * ratio)

        outer = polar(x, y, radius * 0.92, angle)
        inner = polar(x, y, radius * 0.80, angle)

        line(image, [inner, outer], fill, 4)

        label_pos = polar(x, y, radius * 0.68, angle)

        centered_text(
            image,
            str(int(maximum * ratio)),
            label_pos,
            18
        )

    ratio = max(0, min(1, value / maximum))
    angle = math.radians(start + sweep * ratio)

    vector(
        image,
        center,
        polar(x, y, radius * 0.72, angle),
        needle,
        6,
        18
    )

    circle(image, center, 12, needle)

    centered_text(
        image,
        str(value),
        (x, y + radius * 0.45),
        32
    )

    return image


def compass(image, center, radius=120):
    circle(
        image,
        center,
        radius,
        (25, 30, 40, 255),
        (230, 230, 240, 255),
        4
    )

    for i in range(16):
        angle = -math.pi / 2 + i * math.pi / 8

        outer = polar(center[0], center[1], radius * 0.94, angle)
        inner = polar(center[0], center[1],
                      radius * (0.84 if i % 4 else 0.78),
                      angle)

        line(image, [inner, outer],
             (220, 220, 230, 255),
             4 if i % 4 == 0 else 2)

    for label, angle in (
        ("N", -math.pi / 2),
        ("E", 0),
        ("S", math.pi / 2),
        ("W", math.pi)
    ):
        p = polar(
            center[0],
            center[1],
            radius * 0.67,
            angle
        )
        centered_text(image, label, p, 28)

    vector(
        image,
        center,
        polar(
            center[0],
            center[1],
            radius * 0.60,
            -math.pi / 2
        ),
        (230, 70, 70, 255),
        6,
        18
    )

    circle(image, center, 8, (240, 240, 240, 255))

    return image


def timeline(image, events, start, end,
             y=None, fill=(100, 190, 255, 255),
             label_size=24):
    if not events:
        return image

    if y is not None:
        start = (start[0], y)
        end = (end[0], y)

    line(image, [start, end], fill, 5)

    n = len(events)

    for i, event in enumerate(events):
        t = i / max(1, n - 1)
        p = lerp(start, end, t)

        circle(image, p, 10, fill)

        label_y = p[1] - 45 if i % 2 == 0 else p[1] + 45

        centered_text(
            image,
            str(event),
            (p[0], label_y),
            label_size
        )

    return image


def process_diagram(image, steps, start,
                    spacing=220, box_size=(180, 90),
                    fill=(40, 45, 55, 255)):
    if not steps:
        return image

    x, y = start
    boxes = []

    for i, step in enumerate(steps):
        cx = x + i * spacing

        box = (
            cx - box_size[0] / 2,
            y - box_size[1] / 2,
            cx + box_size[0] / 2,
            y + box_size[1] / 2
        )

        flow_box(image, box, str(step), fill=fill)
        boxes.append(box)

        if i:
            vector(
                image,
                (boxes[i - 1][2], y),
                (box[0], y),
                width=4,
                tip_length=14
            )

    return image


def hierarchy(image, levels, start,
               dx=220, dy=110,
               box_size=(140, 70)):
    if not levels:
        return image

    parents = [start]

    for level_index, labels in enumerate(levels):
        if not labels:
            continue

        children = []

        for i, label in enumerate(labels):
            parent = parents[min(
                len(parents) - 1,
                i * len(parents) // len(labels)
            )]

            offset = (
                (i - (len(labels) - 1) / 2) * dx
            )

            x = start[0] + offset
            y = start[1] + (level_index + 1) * dy

            child = (x, y)
            children.append(child)

            flow_box(
                image,
                (
                    x - box_size[0] / 2,
                    y - box_size[1] / 2,
                    x + box_size[0] / 2,
                    y + box_size[1] / 2
                ),
                str(label)
            )

            line(
                image,
                [
                    parent,
                    (x, y - box_size[1] / 2)
                ],
                width=3
            )

        parents = children

    return image


def probability_tree(image, root, branches,
                     dx=180, dy=110,
                     node_radius=25):
    x, y = root

    circle(
        image,
        root,
        node_radius,
        (70, 150, 230, 255),
        (240, 240, 240, 255),
        3
    )

    if not branches:
        return image

    for i, branch in enumerate(branches):
        if len(branch) == 2:
            label, probability = branch
        elif len(branch) >= 3:
            label, probability = branch[:2]
        else:
            continue

        direction = -1 if i % 2 == 0 else 1

        end = (
            x + direction * dx,
            y + dy
        )

        vector(
            image,
            root,
            end,
            width=4,
            tip_length=14
        )

        circle(
            image,
            end,
            node_radius,
            (70, 150, 230, 255),
            (240, 240, 240, 255),
            3
        )

        centered_text(
            image,
            f"{label} ({probability})",
            (end[0], end[1] + node_radius + 22),
            22
        )

    return image


def chemical_bond(image, a, b, order=1,
                  fill=(220, 220, 220, 255),
                  width=6):
    if order not in (1, 2, 3):
        raise ValueError("bond order must be 1, 2 or 3")

    ax, ay = a
    bx, by = b

    dx = bx - ax
    dy = by - ay
    length = math.hypot(dx, dy)

    if length == 0:
        return image

    nx = -dy / length
    ny = dx / length

    offsets = {
        1: [0],
        2: [-8, 8],
        3: [-12, 0, 12]
    }[order]

    for offset in offsets:
        a2 = (ax + nx * offset, ay + ny * offset)
        b2 = (bx + nx * offset, by + ny * offset)
        line(image, [a2, b2], fill, width)

    return image


def molecule_diagram(image, atoms, bonds,
                     radius=35, colors=None,
                     labels=None,
                     bond_width=6):
    for bond in bonds:
        if len(bond) == 2:
            a, b = bond
            order = 1
        else:
            a, b, order = bond[:3]

        chemical_bond(
            image,
            atoms[a],
            atoms[b],
            order,
            width=bond_width
        )

    for i, p in enumerate(atoms):
        color = (
            colors[i]
            if colors and i < len(colors)
            else (90, 170, 240, 255)
        )

        circle(
            image,
            p,
            radius,
            color,
            (240, 240, 240, 255),
            3
        )

        if labels and i < len(labels):
            centered_text(
                image,
                str(labels[i]),
                p,
                22,
                fill=(255, 255, 255, 255)
            )

    return image


def solar_system(image, center, planets,
                 scale=1, orbits=True,
                 sun_radius=45,
                 background=(10, 15, 30, 255)):
    cx, cy = center

    for distance_value, radius, color, label in planets:
        r = distance_value * scale

        if orbits:
            circle(
                image,
                center,
                r,
                None,
                (80, 90, 110, 150),
                2
            )

        px, py = cx + r, cy

        circle(image, (px, py), radius, color)

        centered_text(
            image,
            str(label),
            (px, py + radius + 25),
            20
        )

    circle(
        image,
        center,
        sun_radius,
        (255, 190, 60, 255),
        (255, 230, 120, 255),
        3
    )

    return image


def wave_pulse(image, center, radius=100,
               rings=5, spacing=50,
               fill=(80, 190, 255, 160),
               width=4):
    if rings <= 0:
        return image

    for i in range(rings):
        circle(
            image,
            center,
            radius + i * spacing,
            None,
            fill,
            width
        )

    circle(
        image,
        center,
        max(4, radius * 0.08),
        fill
    )

    return image


def heat_scale(image, box, minimum=0, maximum=100,
               value=50,
               marker_width=5):
    if maximum <= minimum:
        raise ValueError("maximum must be greater than minimum")

    x1, y1, x2, y2 = box
    height = max(1, int(y2 - y1))

    for i in range(height):
        t = i / max(1, height - 1)

        color = (
            int(255 * t),
            int(80 + 120 * (1 - t)),
            int(255 * (1 - t)),
            255
        )

        line(
            image,
            [(x1, y1 + i), (x2, y1 + i)],
            color,
            2
        )

    ratio = max(
        0,
        min(1, (value - minimum) / (maximum - minimum))
    )

    y = y2 - ratio * (y2 - y1)

    line(
        image,
        [(x1 - 15, y), (x2 + 15, y)],
        (255, 255, 255, 255),
        marker_width
    )

    centered_text(
        image,
        str(value),
        (x2 + 45, y),
        22
    )

    centered_text(
        image,
        str(maximum),
        (x2 + 35, y1),
        18
    )

    centered_text(
        image,
        str(minimum),
        (x2 + 35, y2),
        18
    )

    return image