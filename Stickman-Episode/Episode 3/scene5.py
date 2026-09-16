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
FRAME_DIR = os.path.join(ROOT, "scene5_frames")
AUDIO_FILE = os.path.join(ROOT, "scene5_audio.wav")

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


def draw_branch(
    draw,
    x,
    ground_y,
    branch_break=0.0,
    broken=False
):
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

    if not broken:
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

    else:
        remaining = 1.0 - branch_break

        end_x = x + 195 * remaining
        end_y = branch_y - 43 * remaining

        line(
            draw,
            [
                (x, branch_y),
                (x + 105 * remaining, branch_y - 20 * remaining),
                (end_x, end_y)
            ],
            TRUNK_DARK,
            18
        )

        line(
            draw,
            [
                (x, branch_y),
                (x + 105 * remaining, branch_y - 20 * remaining),
                (end_x, end_y)
            ],
            TRUNK,
            11
        )

        broken_x = x + 105 * remaining
        broken_y = branch_y - 20 * remaining

        if branch_break > 0.15:
            draw.line(
                (
                    int(broken_x - 7),
                    int(broken_y - 10),
                    int(broken_x + 9),
                    int(broken_y + 8)
                ),
                fill=(50, 35, 25),
                width=5
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


def draw_leaves(
    draw,
    rng,
    center_x,
    center_y,
    count=28,
    spread=70,
    falling=False,
    progress=0.0
):
    for i in range(count):
        angle = (
            i * 2.399
            + rng.random() * 0.6
        )

        radius = (
            spread
            * math.sqrt(rng.random())
        )

        x = center_x + math.cos(angle) * radius
        y = center_y + math.sin(angle) * radius * 0.65

        if falling:
            y += 100 * progress
            x += 45 * math.sin(
                progress * 5 + i
            )

        size = 5 + 4 * rng.random()

        circle(
            draw,
            x,
            y,
            size,
            LEAF_DARK
        )


def draw_environment(draw):
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

    for x in range(0, W, 20):
        h = int(rng.integers(5, 16))

        draw.line(
            (
                x,
                ground_y,
                x + 3,
                ground_y - h
            ),
            fill=GROUND_DARK,
            width=2
        )

    for _ in range(100):
        x = int(rng.integers(0, W))
        y = int(rng.integers(580, H))
        r = int(rng.integers(2, 5))

        circle(
            draw,
            x,
            y,
            r,
            GROUND_DARK
        )


def draw_stickman(
    draw,
    x,
    foot_y,
    scale=1.0,
    pose="climb",
    phase=0.0,
    look_x=0.0,
    look_y=0.0,
    mouth=0.0,
    blink=False,
    tilt=0.0,
    arm_reach=0.0,
    fall_rotation=0.0
):
    head_r = 29 * scale

    body_length = 145 * scale

    neck_y = foot_y - body_length
    hip_y = foot_y - 65 * scale

    head_x = x + tilt * 13 * scale
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

    if pose == "shock":
        line(
            draw,
            [
                (head_x - 19 * scale, head_y - 19 * scale),
                (head_x - 7 * scale, head_y - 13 * scale)
            ],
            BLACK,
            3 * scale
        )

        line(
            draw,
            [
                (head_x + 7 * scale, head_y - 13 * scale),
                (head_x + 19 * scale, head_y - 19 * scale)
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

    if pose == "reach":
        left_hand_x = x - 42 * scale
        left_hand_y = (
            shoulder_y
            - 55 * scale
        )

        right_hand_x = (
            x
            + 42 * scale
            + 45 * arm_reach * scale
        )

        right_hand_y = (
            shoulder_y
            - 70 * scale
            - 18 * arm_reach * scale
        )

        line(
            draw,
            [
                (x, shoulder_y),
                (
                    x - 25 * scale,
                    shoulder_y - 30 * scale
                ),
                (
                    left_hand_x,
                    left_hand_y
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
                    shoulder_y - 35 * scale
                ),
                (
                    right_hand_x,
                    right_hand_y
                )
            ],
            BLACK,
            7 * scale
        )

        circle(
            draw,
            left_hand_x,
            left_hand_y,
            5 * scale,
            WHITE,
            BLACK,
            2 * scale
        )

        circle(
            draw,
            right_hand_x,
            right_hand_y,
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
                    x - 30 * scale,
                    hip_y + 30 * scale
                ),
                (
                    x - 43 * scale,
                    foot_y - 25 * scale
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
                    hip_y + 30 * scale
                ),
                (
                    x + 43 * scale,
                    foot_y - 42 * scale
                )
            ],
            BLACK,
            8 * scale
        )

    elif pose == "fall":
        arm = math.sin(phase) * 16 * scale

        line(
            draw,
            [
                (x, shoulder_y),
                (
                    x - 38 * scale,
                    shoulder_y - 20 * scale
                ),
                (
                    x - 72 * scale,
                    shoulder_y - 58 * scale + arm
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
                    x + 38 * scale,
                    shoulder_y - 20 * scale
                ),
                (
                    x + 72 * scale,
                    shoulder_y - 58 * scale - arm
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
                    x - 35 * scale,
                    hip_y + 25 * scale
                ),
                (
                    x - 62 * scale,
                    hip_y - 2 * scale
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
                    x + 35 * scale,
                    hip_y + 25 * scale
                ),
                (
                    x + 62 * scale,
                    hip_y - 2 * scale
                )
            ],
            BLACK,
            8 * scale
        )

    elif pose == "hide":
        line(
            draw,
            [
                (x, shoulder_y),
                (
                    x - 35 * scale,
                    shoulder_y + 15 * scale
                ),
                (
                    x - 55 * scale,
                    shoulder_y + 45 * scale
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
                    shoulder_y + 15 * scale
                ),
                (
                    x + 55 * scale,
                    shoulder_y + 45 * scale
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
                    hip_y + 40 * scale
                ),
                (
                    x - 40 * scale,
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
                    hip_y + 40 * scale
                ),
                (
                    x + 40 * scale,
                    foot_y
                )
            ],
            BLACK,
            8 * scale
        )

    else:
        cycle = phase * math.pi * 2

        hand_wave = math.sin(cycle)

        left_hand_x = x - 44 * scale
        left_hand_y = (
            shoulder_y
            - 58 * scale
            - hand_wave * 12 * scale
        )

        right_hand_x = x + 44 * scale
        right_hand_y = (
            shoulder_y
            - 58 * scale
            + hand_wave * 12 * scale
        )

        line(
            draw,
            [
                (x, shoulder_y),
                (
                    x - 27 * scale,
                    shoulder_y - 32 * scale
                ),
                (
                    left_hand_x,
                    left_hand_y
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
                    x + 27 * scale,
                    shoulder_y - 32 * scale
                ),
                (
                    right_hand_x,
                    right_hand_y
                )
            ],
            BLACK,
            7 * scale
        )

        circle(
            draw,
            left_hand_x,
            left_hand_y,
            5 * scale,
            WHITE,
            BLACK,
            2 * scale
        )

        circle(
            draw,
            right_hand_x,
            right_hand_y,
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
                    hip_y + 30 * scale
                ),
                (
                    x - 42 * scale,
                    foot_y - 25 * scale
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
                    hip_y + 30 * scale
                ),
                (
                    x + 42 * scale,
                    foot_y - 40 * scale
                )
            ],
            BLACK,
            8 * scale
        )


def speech_strength(frame):
    start = int(0.45 * FPS)
    end = int(1.85 * FPS)

    if frame < start or frame > end:
        return 0.0

    t = (frame - start) / (end - start)

    signal = (
        0.50
        + 0.32 * math.sin(t * 45)
        + 0.15 * math.sin(t * 82)
        + 0.08 * math.sin(t * 129)
    )

    fade = min(
        1.0,
        t / 0.08,
        (1.0 - t) / 0.08
    )

    return clamp(signal) * fade


def synthesize_audio():
    sample_rate = 22050
    total = int(DURATION * sample_rate)

    audio = np.zeros(
        total,
        dtype=np.float32
    )

    events = [
        (0.45, 1.05, 185, 0.18),
        (1.10, 1.85, 165, 0.21),

        (3.55, 3.70, 125, 0.10),
        (4.05, 4.22, 105, 0.10),

        (4.42, 4.60, 82, 0.11),
        (4.62, 4.84, 58, 0.14),

        (5.10, 5.65, 65, 0.13),
        (5.65, 6.15, 52, 0.11),

        (6.30, 6.80, 72, 0.10)
    ]

    for start, end, base, volume in events:
        a = int(start * sample_rate)
        b = int(end * sample_rate)

        n = b - a

        if n <= 0:
            continue

        tt = np.arange(
            n,
            dtype=np.float32
        ) / sample_rate

        vibrato = (
            4.0
            * np.sin(
                2 * np.pi * 4.0 * tt
            )
        )

        carrier = (
            0.70
            * np.sin(
                2 * np.pi
                * (base + vibrato)
                * tt
            )
            + 0.20
            * np.sin(
                2 * np.pi
                * 2
                * (base + vibrato)
                * tt
            )
            + 0.10
            * np.sin(
                2 * np.pi
                * 3
                * (base + vibrato)
                * tt
            )
        )

        envelope = np.minimum(
            1.0,
            np.minimum(
                np.arange(n)
                / (sample_rate * 0.025),
                np.arange(n, 0, -1)
                / (sample_rate * 0.05)
            )
        )

        audio[a:b] += (
            carrier
            * envelope
            * volume
        )

    rng = np.random.default_rng(515)

    audio += rng.normal(
        0,
        0.002,
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

    draw_environment(draw)

    ground_y = 570
    tree_x = 960

    rng = np.random.default_rng(852)

    branch_break = 0.0

    if 0.57 < t < 0.69:
        branch_break = smooth(
            (t - 0.57) / 0.12
        )

    draw_branch(
        draw,
        tree_x,
        ground_y,
        branch_break=branch_break,
        broken=branch_break > 0
    )

    if t < 0.14:
        p = smooth(t / 0.14)

        x = lerp(
            850,
            875,
            p
        )

        foot_y = (
            ground_y
            - 275
        )

        pose = "climb"

        look_x = 100
        look_y = -120

        mouth = speech_strength(frame)

        tilt = 0.0
        arm_reach = 0.0
        fall_rotation = 0.0

    elif t < 0.27:
        p = smooth(
            (t - 0.14) / 0.13
        )

        x = 875

        foot_y = (
            ground_y
            - 275
        )

        pose = "reach"

        look_x = 130
        look_y = -80

        mouth = speech_strength(frame)

        tilt = 0.0
        arm_reach = p
        fall_rotation = 0.0

    elif t < 0.42:
        p = smooth(
            (t - 0.27) / 0.15
        )

        x = 875

        foot_y = (
            ground_y
            - 275
            - 15 * p
        )

        pose = "reach"

        look_x = 140
        look_y = -65

        mouth = 0.0

        tilt = 0.015 * p
        arm_reach = 1.0
        fall_rotation = 0.0

    elif t < 0.54:
        p = smooth(
            (t - 0.42) / 0.12
        )

        x = 875

        foot_y = (
            ground_y
            - 290
            + 10 * p
        )

        pose = "reach"

        look_x = 115
        look_y = -30

        mouth = 0.0

        tilt = 0.02 * p
        arm_reach = 1.0
        fall_rotation = 0.0

    elif t < 0.61:
        p = smooth(
            (t - 0.54) / 0.07
        )

        x = 875 + 5 * p

        foot_y = (
            ground_y
            - 280
            + 15 * p
        )

        pose = "shock"

        look_x = 100
        look_y = -40

        mouth = 0.9 * p

        tilt = -0.08 * p
        arm_reach = 1.0
        fall_rotation = 0.0

    elif t < 0.72:
        p = ease_in(
            (t - 0.61) / 0.11
        )

        x = (
            880
            + 35 * p
        )

        fall_distance = 145 * p

        foot_y = (
            ground_y
            - 265
            + fall_distance
        )

        pose = "fall"

        look_x = 35
        look_y = 45

        mouth = 0.75

        tilt = -0.10 + 0.08 * p
        arm_reach = 0.0
        fall_rotation = p

    elif t < 0.82:
        p = ease_out(
            (t - 0.72) / 0.10
        )

        x = (
            915
            - 40 * p
        )

        foot_y = (
            ground_y
            - 120
            + 95 * p
        )

        pose = "fall"

        look_x = 15
        look_y = 70

        mouth = 0.70 * (1.0 - p)

        tilt = -0.02 * (1.0 - p)
        arm_reach = 0.0
        fall_rotation = 1.0 - p

    elif t < 0.90:
        p = smooth(
            (t - 0.82) / 0.08
        )

        x = 875

        foot_y = ground_y

        pose = "hide"

        look_x = 0
        look_y = -20

        mouth = 0.0

        tilt = 0.0
        arm_reach = 0.0
        fall_rotation = 0.0

    else:
        p = smooth(
            (t - 0.90) / 0.10
        )

        x = 875

        foot_y = ground_y

        pose = "shock"

        look_x = 80
        look_y = -100

        mouth = 0.0

        tilt = 0.0
        arm_reach = 0.0
        fall_rotation = 0.0

    blink = (
        27 <= frame <= 30
        or 91 <= frame <= 94
        or 154 <= frame <= 157
        or 213 <= frame <= 216
    )

    if 0.64 < t < 0.82:
        draw_leaves(
            draw,
            rng,
            900,
            475,
            count=35,
            spread=85,
            falling=True,
            progress=clamp(
                (t - 0.64) / 0.18
            )
        )

    draw_stickman(
        draw,
        x,
        foot_y,
        scale=1.0,
        pose=pose,
        phase=frame * 0.52,
        look_x=look_x,
        look_y=look_y,
        mouth=mouth,
        blink=blink,
        tilt=tilt,
        arm_reach=arm_reach,
        fall_rotation=fall_rotation
    )

    if t > 0.30:
        p = smooth(
            (t - 0.30) / 0.70
        )

        zoom = 1.0 + 0.055 * p

        crop_w = int(W / zoom)
        crop_h = int(H / zoom)

        left = (W - crop_w) // 2

        vertical_focus = int(
            35 * p
        )

        top = max(
            0,
            (H - crop_h) // 2
            - vertical_focus
        )

        if top + crop_h > H:
            top = H - crop_h

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
    print("Rendering Scene 5...")

    for frame in range(FRAMES):
        render(frame)

    print("Generating audio...")
    synthesize_audio()

    print("Scene 5 complete.")
    print(f"Frames: {FRAME_DIR}")
    print(f"Audio: {AUDIO_FILE}")


if __name__ == "__main__":
    main()
