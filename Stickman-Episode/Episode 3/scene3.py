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
FRAME_DIR = os.path.join(ROOT, "scene3_frames")
AUDIO_FILE = os.path.join(ROOT, "scene3_audio.wav")

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


def draw_tree(draw, x, ground_y, scale=1.0):
    trunk_top = ground_y - 370 * scale
    trunk_w = 105 * scale

    draw.rounded_rectangle(
        (
            int(x - trunk_w / 2),
            int(trunk_top),
            int(x + trunk_w / 2),
            int(ground_y)
        ),
        radius=int(22 * scale),
        fill=TRUNK
    )

    line(
        draw,
        [
            (x - 5 * scale, ground_y),
            (x - 3 * scale, trunk_top + 95 * scale),
            (x - 112 * scale, trunk_top - 5 * scale)
        ],
        TRUNK_DARK,
        17 * scale
    )

    line(
        draw,
        [
            (x + 5 * scale, trunk_top + 145 * scale),
            (x + 112 * scale, trunk_top + 8 * scale)
        ],
        TRUNK_DARK,
        16 * scale
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
            x + ox * scale,
            trunk_top + oy * scale,
            r * scale,
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
            x + ox * scale,
            trunk_top + oy * scale,
            r * scale,
            LEAF
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

    rng = np.random.default_rng(321)

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


def draw_stickman(
    draw,
    x,
    foot_y,
    scale=1.0,
    pose="idle",
    phase=0.0,
    look_x=0.0,
    look_y=0.0,
    mouth=0.0,
    blink=False,
    lean=0.0,
    climb_progress=0.0
):
    head_r = 29 * scale

    neck_y = foot_y - 145 * scale
    hip_y = foot_y - 65 * scale

    head_x = x + lean * 13 * scale
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

    max_eye = 5.5 * scale

    eye_dx = (
        clamp(look_x / distance, -1, 1)
        * max_eye
    )

    eye_dy = (
        clamp(look_y / distance, -1, 1)
        * max_eye
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

    if pose == "climb":
        brow_y = head_y - 19 * scale

        line(
            draw,
            [
                (head_x - 19 * scale, brow_y + 1 * scale),
                (head_x - 7 * scale, brow_y - 3 * scale)
            ],
            BLACK,
            3 * scale
        )

        line(
            draw,
            [
                (head_x + 7 * scale, brow_y - 3 * scale),
                (head_x + 19 * scale, brow_y + 1 * scale)
            ],
            BLACK,
            3 * scale
        )
    elif pose == "fall":
        line(
            draw,
            [
                (head_x - 19 * scale, head_y - 18 * scale),
                (head_x - 7 * scale, head_y - 13 * scale)
            ],
            BLACK,
            3 * scale
        )

        line(
            draw,
            [
                (head_x + 7 * scale, head_y - 13 * scale),
                (head_x + 19 * scale, head_y - 18 * scale)
            ],
            BLACK,
            3 * scale
        )
    else:
        line(
            draw,
            [
                (head_x - 19 * scale, head_y - 16 * scale),
                (head_x - 7 * scale, head_y - 20 * scale)
            ],
            BLACK,
            3 * scale
        )

        line(
            draw,
            [
                (head_x + 7 * scale, head_y - 20 * scale),
                (head_x + 19 * scale, head_y - 16 * scale)
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
    elif mouth > 0.38:
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

    if pose == "climb":
        reach = climb_progress

        left_hand_x = x - 43 * scale
        left_hand_y = (
            shoulder_y
            - (43 + 12 * math.sin(reach * math.pi)) * scale
        )

        right_hand_x = x + 43 * scale
        right_hand_y = (
            shoulder_y
            - (72 - 12 * math.sin(reach * math.pi)) * scale
        )

        line(
            draw,
            [
                (x, shoulder_y),
                (
                    x - 28 * scale,
                    shoulder_y - 27 * scale
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
                    x + 25 * scale,
                    shoulder_y - 38 * scale
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

        leg_motion = math.sin(
            phase
        ) * 9 * scale

        line(
            draw,
            [
                (x, hip_y),
                (
                    x - 28 * scale,
                    hip_y + 30 * scale
                ),
                (
                    x - 40 * scale + leg_motion,
                    foot_y - 5 * scale
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
                    x + 40 * scale - leg_motion,
                    foot_y - 27 * scale
                )
            ],
            BLACK,
            8 * scale
        )

    elif pose == "fall":
        arm = math.sin(phase) * 15 * scale

        line(
            draw,
            [
                (x, shoulder_y),
                (
                    x - 37 * scale,
                    shoulder_y - 25 * scale
                ),
                (
                    x - 70 * scale,
                    shoulder_y - 48 * scale + arm
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
                    x + 36 * scale,
                    shoulder_y - 20 * scale
                ),
                (
                    x + 70 * scale,
                    shoulder_y - 43 * scale - arm
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
                    hip_y + 28 * scale
                ),
                (
                    x - 60 * scale,
                    hip_y + 5 * scale
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
                    x + 34 * scale,
                    hip_y + 28 * scale
                ),
                (
                    x + 60 * scale,
                    hip_y + 4 * scale
                )
            ],
            BLACK,
            8 * scale
        )

    elif pose == "recover":
        arm = math.sin(phase) * 5 * scale

        line(
            draw,
            [
                (x, shoulder_y),
                (
                    x - 30 * scale,
                    shoulder_y - 10 * scale
                ),
                (
                    x - 55 * scale,
                    shoulder_y + 23 * scale + arm
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
                    x + 31 * scale,
                    shoulder_y - 8 * scale
                ),
                (
                    x + 55 * scale,
                    shoulder_y + 22 * scale - arm
                )
            ],
            BLACK,
            7 * scale
        )

        leg = math.sin(phase) * 10 * scale

        line(
            draw,
            [
                (x, hip_y),
                (
                    x - 22 * scale,
                    hip_y + 55 * scale
                ),
                (
                    x - 32 * scale - leg,
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
                    x + 22 * scale,
                    hip_y + 55 * scale
                ),
                (
                    x + 32 * scale + leg,
                    foot_y
                )
            ],
            BLACK,
            8 * scale
        )

    else:
        arm = math.sin(phase) * 20 * scale

        line(
            draw,
            [
                (x, shoulder_y),
                (
                    x - 35 * scale + arm,
                    shoulder_y + 45 * scale
                ),
                (
                    x - 48 * scale + arm,
                    shoulder_y + 84 * scale
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
                    x + 35 * scale - arm,
                    shoulder_y + 45 * scale
                ),
                (
                    x + 48 * scale - arm,
                    shoulder_y + 84 * scale
                )
            ],
            BLACK,
            7 * scale
        )

        leg = math.sin(phase) * 20 * scale

        line(
            draw,
            [
                (x, hip_y),
                (
                    x - 20 * scale - leg,
                    hip_y + 58 * scale
                ),
                (
                    x - 30 * scale - leg,
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
                    x + 20 * scale + leg,
                    hip_y + 58 * scale
                ),
                (
                    x + 30 * scale + leg,
                    foot_y
                )
            ],
            BLACK,
            8 * scale
        )


def mouth_animation(frame):
    start = int(0.8 * FPS)
    end = int(2.15 * FPS)

    if frame < start or frame > end:
        return 0.0

    t = (frame - start) / (end - start)

    signal = (
        0.50
        + 0.32 * math.sin(t * 43)
        + 0.15 * math.sin(t * 79)
        + 0.08 * math.sin(t * 121)
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
        (0.80, 1.25, 190, 0.18),
        (1.30, 2.15, 165, 0.22),

        (4.45, 4.62, 95, 0.13),
        (5.02, 5.24, 115, 0.12),

        (5.60, 5.90, 75, 0.11),
        (6.05, 6.45, 68, 0.10)
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
                2 * np.pi * 4.2 * tt
            )
        )

        carrier = (
            0.68
            * np.sin(
                2 * np.pi
                * (base + vibrato)
                * tt
            )
            + 0.21
            * np.sin(
                2 * np.pi
                * 2
                * (base + vibrato)
                * tt
            )
            + 0.11
            * np.sin(
                2 * np.pi
                * 3
                * (base + vibrato)
                * tt
            )
        )

        syllable = (
            0.55
            + 0.45
            * np.sin(
                2 * np.pi * 5.0 * tt
            )
        )

        attack = np.minimum(
            1.0,
            np.arange(n)
            / (sample_rate * 0.035)
        )

        release = np.minimum(
            1.0,
            np.arange(n, 0, -1)
            / (sample_rate * 0.055)
        )

        envelope = np.minimum(
            attack,
            release
        )

        audio[a:b] += (
            carrier
            * syllable
            * envelope
            * volume
        )

    rng = np.random.default_rng(44)

    audio += rng.normal(
        0,
        0.0025,
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

    draw_tree(
        draw,
        tree_x,
        ground_y
    )

    mouth = mouth_animation(frame)

    if t < 0.14:
        p = smooth(t / 0.14)

        x = lerp(850, 790, p)

        foot_y = ground_y

        pose = "recover"

        look_x = tree_x - x
        look_y = -100

        lean = 0.0

    elif t < 0.26:
        p = smooth(
            (t - 0.14) / 0.12
        )

        x = lerp(790, 840, p)

        foot_y = ground_y

        pose = "idle"

        look_x = tree_x - x
        look_y = -130

        lean = 0.0

    elif t < 0.36:
        p = smooth(
            (t - 0.26) / 0.10
        )

        x = 840

        foot_y = ground_y - 5 * p

        pose = "climb"

        look_x = tree_x - x
        look_y = -145

        lean = 0.0

    elif t < 0.56:
        p = smooth(
            (t - 0.36) / 0.20
        )

        x = 840

        climb_height = 185 * p

        foot_y = ground_y - climb_height

        pose = "climb"

        look_x = tree_x - x
        look_y = -170

        lean = 0.015

    elif t < 0.64:
        p = smooth(
            (t - 0.56) / 0.08
        )

        x = 840

        foot_y = ground_y - 185

        pose = "climb"

        look_x = 20
        look_y = 130

        lean = -0.02 * p

    elif t < 0.72:
        p = smooth(
            (t - 0.64) / 0.08
        )

        x = 840 + 7 * p

        foot_y = (
            ground_y
            - 185
            + 35 * p
        )

        pose = "fall"

        look_x = 30
        look_y = 70

        lean = -0.16 * p

    elif t < 0.84:
        p = ease_out(
            (t - 0.72) / 0.12
        )

        x = 847 + 18 * p

        foot_y = (
            ground_y
            - 150
            + 140 * p
        )

        pose = "fall"

        look_x = 35
        look_y = 40

        lean = -0.16 + 0.16 * p

    else:
        p = smooth(
            (t - 0.84) / 0.16
        )

        x = lerp(
            865,
            850,
            p
        )

        foot_y = ground_y

        pose = "recover"

        look_x = tree_x - x
        look_y = -130

        lean = 0.0

    blink = (
        29 <= frame <= 32
        or 87 <= frame <= 90
        or 143 <= frame <= 146
        or 201 <= frame <= 204
    )

    climb_progress = clamp(
        (foot_y - (ground_y - 185))
        / 185
    )

    draw_stickman(
        draw,
        x,
        foot_y,
        scale=1.0,
        pose=pose,
        phase=frame * 0.48,
        look_x=look_x,
        look_y=look_y,
        mouth=mouth,
        blink=blink,
        lean=lean,
        climb_progress=climb_progress
    )

    if t > 0.82:
        p = smooth(
            (t - 0.82) / 0.18
        )

        zoom = 1.0 + 0.025 * p

        crop_w = int(W / zoom)
        crop_h = int(H / zoom)

        left = (W - crop_w) // 2
        top = (H - crop_h) // 2

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
    print("Rendering Scene 3...")

    for frame in range(FRAMES):
        render(frame)

    print("Generating audio...")
    synthesize_audio()

    print("Scene 3 complete.")
    print(f"Frames: {FRAME_DIR}")
    print(f"Audio: {AUDIO_FILE}")


if __name__ == "__main__":
    main()
