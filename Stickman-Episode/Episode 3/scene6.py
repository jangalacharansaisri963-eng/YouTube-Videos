import math
import os
import wave

import numpy as np
from PIL import Image, ImageDraw

W, H = 1280, 720
FPS = 30
DURATION = 8
FRAMES = FPS * DURATION

ROOT = os.path.dirname(os.path.abspath(__file__))
FRAME_DIR = os.path.join(ROOT, "scene6_frames")
AUDIO_FILE = os.path.join(ROOT, "scene6_audio.wav")

os.makedirs(FRAME_DIR, exist_ok=True)

BLACK = (18, 18, 22)
WHITE = (248, 248, 248)

SKY_TOP = np.array([145, 207, 248], dtype=np.float32)
SKY_BOTTOM = np.array([225, 242, 250], dtype=np.float32)

GROUND = (82, 151, 72)
GROUND_DARK = (53, 111, 50)

TRUNK = (105, 67, 39)
TRUNK_DARK = (72, 44, 28)

LEAF = (48, 135, 62)
LEAF_DARK = (34, 103, 47)

LADDER = (180, 116, 62)
LADDER_DARK = (116, 70, 40)

SHADOW = (57, 108, 50)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def smooth(x):
    x = clamp(x)
    return x * x * (3.0 - 2.0 * x)


def ease_in(x):
    x = clamp(x)
    return x * x


def ease_out(x):
    x = clamp(x)
    return 1.0 - (1.0 - x) ** 2


def lerp(a, b, t):
    return a + (b - a) * smooth(t)


def circle(draw, x, y, r, fill, outline=None, width=1):
    draw.ellipse(
        (
            int(x - r),
            int(y - r),
            int(x + r),
            int(y + r)
        ),
        fill=fill,
        outline=outline,
        width=max(1, int(width))
    )


def line(draw, points, fill=BLACK, width=7):
    draw.line(
        [(int(x), int(y)) for x, y in points],
        fill=fill,
        width=max(1, int(width)),
        joint="curve"
    )


def draw_cloud(draw, x, y, scale):
    for ox, oy, r in [
        (-42, 8, 31),
        (0, -12, 42),
        (43, 8, 31)
    ]:
        circle(
            draw,
            x + ox * scale,
            y + oy * scale,
            r * scale,
            (248, 250, 251)
        )


def draw_tree(draw, x, ground_y):
    trunk_top = ground_y - 370

    draw.rounded_rectangle(
        (
            int(x - 52),
            int(trunk_top),
            int(x + 52),
            int(ground_y)
        ),
        radius=20,
        fill=TRUNK
    )

    line(
        draw,
        [
            (x - 5, ground_y),
            (x - 3, trunk_top + 95),
            (x - 112, trunk_top - 5)
        ],
        TRUNK_DARK,
        17
    )

    branch_y = trunk_top + 145

    line(
        draw,
        [
            (x, branch_y),
            (x + 105, branch_y - 20),
            (x + 195, branch_y - 43)
        ],
        TRUNK_DARK,
        18
    )

    line(
        draw,
        [
            (x, branch_y),
            (x + 105, branch_y - 20),
            (x + 195, branch_y - 43)
        ],
        TRUNK,
        11
    )

    for ox, oy, r in [
        (-125, -15, 82),
        (-75, -85, 105),
        (0, -120, 118),
        (80, -90, 105),
        (135, -20, 82),
        (-15, -35, 130)
    ]:
        circle(
            draw,
            x + ox,
            trunk_top + oy,
            r,
            LEAF_DARK
        )

    for ox, oy, r in [
        (-105, -30, 70),
        (-50, -95, 88),
        (20, -100, 98),
        (90, -55, 80),
        (0, -35, 105)
    ]:
        circle(
            draw,
            x + ox,
            trunk_top + oy,
            r,
            LEAF
        )


def draw_ladder(draw, x, ground_y, scale=1.0, angle=0.0):
    top_y = ground_y - 285 * scale
    bottom_y = ground_y

    rail_dx = 58 * scale

    left_top = (x - rail_dx, top_y)
    left_bottom = (x - 28 * scale, bottom_y)

    right_top = (x + rail_dx, top_y)
    right_bottom = (x + 28 * scale, bottom_y)

    line(
        draw,
        [left_bottom, left_top],
        LADDER_DARK,
        int(15 * scale)
    )

    line(
        draw,
        [right_bottom, right_top],
        LADDER_DARK,
        int(15 * scale)
    )

    line(
        draw,
        [left_bottom, left_top],
        LADDER,
        int(9 * scale)
    )

    line(
        draw,
        [right_bottom, right_top],
        LADDER,
        int(9 * scale)
    )

    for i in range(8):
        p = i / 7

        y = lerp(
            bottom_y - 18 * scale,
            top_y + 18 * scale,
            p
        )

        left_x = lerp(
            x - 28 * scale,
            x - rail_dx,
            p
        )

        right_x = lerp(
            x + 28 * scale,
            x + rail_dx,
            p
        )

        line(
            draw,
            [
                (left_x, y),
                (right_x, y)
            ],
            LADDER_DARK,
            int(9 * scale)
        )

        line(
            draw,
            [
                (left_x, y),
                (right_x, y)
            ],
            LADDER,
            int(5 * scale)
        )


def draw_dust(draw, x, y, progress):
    count = 22

    for i in range(count):
        a = i * 2.399

        radius = (
            12
            + 58 * smooth(progress)
        ) * (
            0.55
            + 0.45 * ((i % 5) / 4)
        )

        px = (
            x
            + math.cos(a) * radius
        )

        py = (
            y
            + math.sin(a) * radius * 0.35
            - 22 * smooth(progress)
        )

        size = (
            3
            + 5 * (1.0 - progress)
        )

        circle(
            draw,
            px,
            py,
            size,
            (158, 174, 120)
        )


def draw_leaves(draw, x, y, progress):
    for i in range(24):
        a = i * 2.41

        distance = (
            20
            + 85 * smooth(progress)
        )

        px = (
            x
            + math.cos(a) * distance
        )

        py = (
            y
            + math.sin(a) * distance * 0.55
            - 35 * progress
        )

        size = 4 + (i % 3)

        circle(
            draw,
            px,
            py,
            size,
            LEAF_DARK
        )


def draw_stickman(
    draw,
    x,
    foot_y,
    scale=1.0,
    pose="stand",
    phase=0.0,
    look_x=0.0,
    look_y=0.0,
    mouth=0.0,
    blink=False
):
    head_r = 29 * scale

    body_length = 145 * scale

    neck_y = foot_y - body_length
    hip_y = foot_y - 65 * scale

    head_x = x
    head_y = neck_y - 38 * scale

    shoulder_y = neck_y + 12 * scale

    circle(
        draw,
        x,
        foot_y + 9 * scale,
        43 * scale,
        SHADOW
    )

    circle(
        draw,
        head_x,
        head_y,
        head_r,
        WHITE,
        BLACK,
        6 * scale
    )

    eye_y = head_y - 3 * scale

    distance = max(
        1.0,
        math.hypot(look_x, look_y)
    )

    eye_limit = 5.5 * scale

    eye_dx = (
        clamp(look_x / distance, -1, 1)
        * eye_limit
    )

    eye_dy = (
        clamp(look_y / distance, -1, 1)
        * eye_limit
    )

    if blink:
        line(
            draw,
            [
                (head_x - 18 * scale, eye_y),
                (head_x - 7 * scale, eye_y)
            ],
            BLACK,
            3 * scale
        )

        line(
            draw,
            [
                (head_x + 7 * scale, eye_y),
                (head_x + 18 * scale, eye_y)
            ],
            BLACK,
            3 * scale
        )
    else:
        for ex in (-12, 12):
            circle(
                draw,
                head_x + ex * scale,
                eye_y,
                4 * scale,
                BLACK
            )

            circle(
                draw,
                head_x + ex * scale + eye_dx,
                eye_y + eye_dy,
                1.6 * scale,
                WHITE
            )

    if pose == "annoyed":
        line(
            draw,
            [
                (head_x - 19 * scale, head_y - 20 * scale),
                (head_x - 7 * scale, head_y - 14 * scale)
            ],
            BLACK,
            4 * scale
        )

        line(
            draw,
            [
                (head_x + 7 * scale, head_y - 14 * scale),
                (head_x + 19 * scale, head_y - 20 * scale)
            ],
            BLACK,
            4 * scale
        )

    elif pose == "idea":
        line(
            draw,
            [
                (head_x - 19 * scale, head_y - 14 * scale),
                (head_x - 7 * scale, head_y - 19 * scale)
            ],
            BLACK,
            3 * scale
        )

        line(
            draw,
            [
                (head_x + 7 * scale, head_y - 19 * scale),
                (head_x + 19 * scale, head_y - 14 * scale)
            ],
            BLACK,
            3 * scale
        )

    else:
        line(
            draw,
            [
                (head_x - 19 * scale, head_y - 18 * scale),
                (head_x - 7 * scale, head_y - 21 * scale)
            ],
            BLACK,
            3 * scale
        )

        line(
            draw,
            [
                (head_x + 7 * scale, head_y - 21 * scale),
                (head_x + 19 * scale, head_y - 18 * scale)
            ],
            BLACK,
            3 * scale
        )

    mouth_y = head_y + 15 * scale

    if mouth > 0.72:
        draw.ellipse(
            (
                int(head_x - 12 * scale),
                int(mouth_y - 4 * scale),
                int(head_x + 12 * scale),
                int(mouth_y + 15 * scale)
            ),
            fill=BLACK
        )
    elif mouth > 0.35:
        draw.ellipse(
            (
                int(head_x - 10 * scale),
                int(mouth_y),
                int(head_x + 10 * scale),
                int(mouth_y + 9 * scale)
            ),
            fill=BLACK
        )
    else:
        line(
            draw,
            [
                (head_x - 8 * scale, mouth_y + 2 * scale),
                (head_x + 8 * scale, mouth_y + 2 * scale)
            ],
            BLACK,
            3 * scale
        )

    line(
        draw,
        [
            (x, neck_y),
            (x, hip_y)
        ],
        BLACK,
        8 * scale
    )

    if pose == "walk":
        cycle = phase * math.pi * 2

        swing = math.sin(cycle) * 20 * scale

        line(
            draw,
            [
                (x, shoulder_y),
                (
                    x - 30 * scale,
                    shoulder_y + swing * 0.45
                ),
                (
                    x - 45 * scale,
                    shoulder_y + 42 * scale + swing
                )
            ],
            BLACK,
            7 * scale
        )

        line(
            draw,
            [
                (x, shoulder_y),
                (
                    x + 30 * scale,
                    shoulder_y - swing * 0.45
                ),
                (
                    x + 45 * scale,
                    shoulder_y + 42 * scale - swing
                )
            ],
            BLACK,
            7 * scale
        )

        line(
            draw,
            [
                (x, hip_y),
                (
                    x - 28 * scale,
                    hip_y + 35 * scale
                ),
                (
                    x - 42 * scale - swing * 0.4,
                    foot_y
                )
            ],
            BLACK,
            8 * scale
        )

        line(
            draw,
            [
                (x, hip_y),
                (
                    x + 28 * scale,
                    hip_y + 35 * scale
                ),
                (
                    x + 42 * scale + swing * 0.4,
                    foot_y
                )
            ],
            BLACK,
            8 * scale
        )

    elif pose == "idea":
        line(
            draw,
            [
                (x, shoulder_y),
                (
                    x - 35 * scale,
                    shoulder_y + 20 * scale
                ),
                (
                    x - 48 * scale,
                    shoulder_y + 50 * scale
                )
            ],
            BLACK,
            7 * scale
        )

        line(
            draw,
            [
                (x, shoulder_y),
                (
                    x + 28 * scale,
                    shoulder_y - 28 * scale
                ),
                (
                    x + 35 * scale,
                    shoulder_y - 60 * scale
                )
            ],
            BLACK,
            7 * scale
        )

        circle(
            draw,
            x + 35 * scale,
            shoulder_y - 60 * scale,
            5 * scale,
            WHITE,
            BLACK,
            2 * scale
        )

        line(
            draw,
            [
                (x, hip_y),
                (
                    x - 29 * scale,
                    hip_y + 35 * scale
                ),
                (
                    x - 42 * scale,
                    foot_y
                )
            ],
            BLACK,
            8 * scale
        )

        line(
            draw,
            [
                (x, hip_y),
                (
                    x + 29 * scale,
                    hip_y + 35 * scale
                ),
                (
                    x + 42 * scale,
                    foot_y
                )
            ],
            BLACK,
            8 * scale
        )

    else:
        line(
            draw,
            [
                (x, shoulder_y),
                (
                    x - 35 * scale,
                    shoulder_y + 20 * scale
                ),
                (
                    x - 50 * scale,
                    shoulder_y + 50 * scale
                )
            ],
            BLACK,
            7 * scale
        )

        line(
            draw,
            [
                (x, shoulder_y),
                (
                    x + 35 * scale,
                    shoulder_y + 20 * scale
                ),
                (
                    x + 50 * scale,
                    shoulder_y + 50 * scale
                )
            ],
            BLACK,
            7 * scale
        )

        line(
            draw,
            [
                (x, hip_y),
                (
                    x - 30 * scale,
                    hip_y + 35 * scale
                ),
                (
                    x - 42 * scale,
                    foot_y
                )
            ],
            BLACK,
            8 * scale
        )

        line(
            draw,
            [
                (x, hip_y),
                (
                    x + 30 * scale,
                    hip_y + 35 * scale
                ),
                (
                    x + 42 * scale,
                    foot_y
                )
            ],
            BLACK,
            8 * scale
        )


def synthesize_audio():
    sample_rate = 22050
    total = int(DURATION * sample_rate)

    audio = np.zeros(
        total,
        dtype=np.float32
    )

    def add_tone(start, end, frequency, volume):
        a = int(start * sample_rate)
        b = int(end * sample_rate)

        if b <= a:
            return

        n = b - a

        tt = np.arange(
            n,
            dtype=np.float32
        ) / sample_rate

        tone = (
            np.sin(
                2 * np.pi
                * frequency
                * tt
            )
            + 0.25
            * np.sin(
                2 * np.pi
                * frequency
                * 2
                * tt
            )
        )

        attack = min(
            1.0,
            np.arange(n)
            / (sample_rate * 0.025)
        )

        release = min(
            1.0,
            np.arange(n, 0, -1)
            / (sample_rate * 0.08)
        )

        envelope = np.minimum(
            attack,
            release
        )

        audio[a:b] += (
            tone
            * envelope
            * volume
        )

    add_tone(0.55, 0.82, 75, 0.13)
    add_tone(0.88, 1.15, 62, 0.10)

    add_tone(3.05, 3.20, 180, 0.15)
    add_tone(3.22, 3.40, 260, 0.13)
    add_tone(3.42, 3.66, 360, 0.15)

    add_tone(4.55, 4.72, 480, 0.15)
    add_tone(4.74, 4.98, 620, 0.17)

    add_tone(5.15, 5.30, 400, 0.12)
    add_tone(5.35, 5.52, 300, 0.11)

    add_tone(6.35, 6.55, 190, 0.12)
    add_tone(6.60, 7.05, 250, 0.16)

    rng = np.random.default_rng(615)

    audio += rng.normal(
        0,
        0.0015,
        total
    ).astype(np.float32)

    audio = np.clip(
        audio,
        -1.0,
        1.0
    )

    pcm = (
        audio * 32767
    ).astype(np.int16)

    with wave.open(
        AUDIO_FILE,
        "wb"
    ) as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(
            pcm.tobytes()
        )


def render(frame):
    t = frame / (FRAMES - 1)

    y = np.arange(
        H,
        dtype=np.float32
    )[:, None]

    q = y / H

    gradient = (
        SKY_TOP * (1 - q[..., None])
        + SKY_BOTTOM * q[..., None]
    )

    arr = np.broadcast_to(
        gradient,
        (H, W, 3)
    ).copy()

    img = Image.fromarray(
        np.clip(
            arr,
            0,
            255
        ).astype(np.uint8),
        "RGB"
    )

    draw = ImageDraw.Draw(img)

    circle(
        draw,
        1080,
        105,
        58,
        (255, 226, 135)
    )

    draw_cloud(
        draw,
        180,
        130,
        1.0
    )

    draw_cloud(
        draw,
        470,
        95,
        0.75
    )

    draw_cloud(
        draw,
        805,
        165,
        0.9
    )

    ground_y = 570

    draw.rectangle(
        (0, ground_y, W, H),
        fill=GROUND
    )

    draw.line(
        (0, ground_y, W, ground_y),
        fill=GROUND_DARK,
        width=7
    )

    rng = np.random.default_rng(741)

    for xg in range(0, W, 20):
        h = int(rng.integers(5, 16))

        draw.line(
            (
                xg,
                ground_y,
                xg + 3,
                ground_y - h
            ),
            fill=GROUND_DARK,
            width=2
        )

    for _ in range(100):
        xg = int(rng.integers(0, W))
        yg = int(rng.integers(580, H))
        r = int(rng.integers(2, 5))

        circle(
            draw,
            xg,
            yg,
            r,
            GROUND_DARK
        )

    tree_x = 1000

    draw_tree(
        draw,
        tree_x,
        ground_y
    )

    ladder_x = 590

    if t < 0.16:
        p = smooth(t / 0.16)

        x = lerp(
            880,
            850,
            p
        )

        pose = "annoyed"
        look_x = 120
        look_y = -90
        mouth = 0.0

    elif t < 0.30:
        p = smooth(
            (t - 0.16) / 0.14
        )

        x = lerp(
            850,
            820,
            p
        )

        pose = "annoyed"
        look_x = 145
        look_y = -75
        mouth = 0.0

    elif t < 0.43:
        p = smooth(
            (t - 0.30) / 0.13
        )

        x = lerp(
            820,
            735,
            p
        )

        pose = "walk"
        look_x = -120
        look_y = 10
        mouth = 0.0

    elif t < 0.52:
        p = smooth(
            (t - 0.43) / 0.09
        )

        x = lerp(
            735,
            700,
            p
        )

        pose = "walk"
        look_x = -130
        look_y = 5
        mouth = 0.0

    elif t < 0.62:
        p = smooth(
            (t - 0.52) / 0.10
        )

        x = 700

        pose = "idea"
        look_x = -120
        look_y = -100
        mouth = 0.35 + 0.45 * p

    elif t < 0.72:
        p = smooth(
            (t - 0.62) / 0.10
        )

        x = 700

        pose = "idea"
        look_x = -110
        look_y = -125
        mouth = 0.75

    elif t < 0.83:
        p = smooth(
            (t - 0.72) / 0.11
        )

        x = lerp(
            700,
            625,
            p
        )

        pose = "walk"
        look_x = -75
        look_y = -120
        mouth = 0.0

    elif t < 0.90:
        p = smooth(
            (t - 0.83) / 0.07
        )

        x = lerp(
            625,
            595,
            p
        )

        pose = "idea"
        look_x = -20
        look_y = -135
        mouth = 0.0

    else:
        p = smooth(
            (t - 0.90) / 0.10
        )

        x = 595

        pose = "idea"
        look_x = 20
        look_y = -145
        mouth = 0.15

    foot_y = ground_y

    draw_ladder(
        draw,
        ladder_x,
        ground_y,
        scale=1.0
    )

    if 0.02 < t < 0.18:
        p = clamp(
            (t - 0.02) / 0.16
        )

        draw_dust(
            draw,
            875,
            ground_y - 5,
            p
        )

        draw_leaves(
            draw,
            875,
            ground_y - 10,
            p
        )

    blink = (
        31 <= frame <= 33
        or 88 <= frame <= 90
        or 146 <= frame <= 148
        or 204 <= frame <= 206
    )

    draw_stickman(
        draw,
        x,
        foot_y,
        scale=1.0,
        pose=pose,
        phase=frame / FPS,
        look_x=look_x,
        look_y=look_y,
        mouth=mouth,
        blink=blink
    )

    if t > 0.84:
        p = smooth(
            (t - 0.84) / 0.16
        )

        zoom = 1.0 + 0.065 * p

        crop_w = int(W / zoom)
        crop_h = int(H / zoom)

        focus_x = int(
            640
            + (595 - 640) * p
        )

        focus_y = int(
            360
            + 20 * p
        )

        left = max(
            0,
            min(
                W - crop_w,
                focus_x - crop_w // 2
            )
        )

        top = max(
            0,
            min(
                H - crop_h,
                focus_y - crop_h // 2
            )
        )

        img = img.crop(
            (
                left,
                top,
                left + crop_w,
                top + crop_h
            )
        ).resize(
            (W, H),
            Image.Resampling.LANCZOS
        )

    filename = os.path.join(
        FRAME_DIR,
        f"frame_{frame:04d}.png"
    )

    img.save(
        filename,
        "PNG"
    )

    return filename


def main():
    print("Rendering Scene 6...")

    for frame in range(FRAMES):
        render(frame)

    print("Generating audio...")
    synthesize_audio()

    print("Scene 6 complete.")
    print(f"Frames: {FRAME_DIR}")
    print(f"Audio: {AUDIO_FILE}")


if __name__ == "__main__":
    main()
