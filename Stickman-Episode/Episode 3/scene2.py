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
FRAME_DIR = os.path.join(ROOT, "scene2_frames")
AUDIO_FILE = os.path.join(ROOT, "scene2_audio.wav")

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
    return 1.0 - (1.0 - x) * (1.0 - x)


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


def draw_leaf_scatter(draw, rng, count=90):
    for _ in range(count):
        x = int(rng.integers(0, W))
        y = int(rng.integers(575, H))

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
    phase=0.0,
    pose="idle",
    look_x=0.0,
    look_y=0.0,
    mouth=0.0,
    blink=False,
    tilt=0.0
):
    head_r = 29 * scale

    body_height = 145 * scale

    neck_x = x
    neck_y = foot_y - body_height

    head_x = x + math.sin(tilt) * 15 * scale
    head_y = neck_y - 38 * scale

    shoulder_y = neck_y + 12 * scale
    hip_y = foot_y - 65 * scale

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

    dx = look_x
    dy = look_y
    distance = max(1.0, math.hypot(dx, dy))

    eye_limit = 5.5 * scale
    eye_dx = clamp(dx / distance, -1, 1) * eye_limit
    eye_dy = clamp(dy / distance, -1, 1) * eye_limit

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
        brow_y = head_y - 20 * scale

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

    if mouth > 0.7:
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
            (neck_x, neck_y),
            (x, hip_y)
        ],
        BLACK,
        8 * scale
    )

    if pose == "approach":
        arm_wave = math.sin(phase) * 7 * scale

        line(
            draw,
            [
                (x, shoulder_y),
                (x - 32 * scale, shoulder_y + 35 * scale),
                (x - 45 * scale, shoulder_y + 75 * scale + arm_wave)
            ],
            BLACK,
            7 * scale
        )

        line(
            draw,
            [
                (x, shoulder_y),
                (x + 30 * scale, shoulder_y + 30 * scale),
                (x + 48 * scale, shoulder_y + 67 * scale - arm_wave)
            ],
            BLACK,
            7 * scale
        )

        leg = math.sin(phase) * 20 * scale

        line(
            draw,
            [
                (x, hip_y),
                (x - 20 * scale - leg, hip_y + 58 * scale),
                (x - 30 * scale - leg, foot_y)
            ],
            BLACK,
            8 * scale
        )

        line(
            draw,
            [
                (x, hip_y),
                (x + 20 * scale + leg, hip_y + 58 * scale),
                (x + 30 * scale + leg, foot_y)
            ],
            BLACK,
            8 * scale
        )

    elif pose == "climb":
        hand_left_x = x - 43 * scale
        hand_left_y = shoulder_y - 45 * scale

        hand_right_x = x + 43 * scale
        hand_right_y = shoulder_y - 70 * scale

        line(
            draw,
            [
                (x, shoulder_y),
                (x - 28 * scale, shoulder_y - 27 * scale),
                (hand_left_x, hand_left_y)
            ],
            BLACK,
            7 * scale
        )

        line(
            draw,
            [
                (x, shoulder_y),
                (x + 25 * scale, shoulder_y - 38 * scale),
                (hand_right_x, hand_right_y)
            ],
            BLACK,
            7 * scale
        )

        circle(
            draw,
            hand_left_x,
            hand_left_y,
            5 * scale,
            WHITE,
            BLACK,
            2 * scale
        )

        circle(
            draw,
            hand_right_x,
            hand_right_y,
            5 * scale,
            WHITE,
            BLACK,
            2 * scale
        )

        leg_phase = phase

        left_knee = (
            x - 27 * scale,
            hip_y + 34 * scale
        )

        right_knee = (
            x + 27 * scale,
            hip_y + 30 * scale
        )

        line(
            draw,
            [
                (x, hip_y),
                left_knee,
                (
                    x - 39 * scale,
                    foot_y - 8 * scale
                )
            ],
            BLACK,
            8 * scale
        )

        line(
            draw,
            [
                (x, hip_y),
                right_knee,
                (
                    x + 40 * scale,
                    foot_y - 25 * scale
                )
            ],
            BLACK,
            8 * scale
        )

    elif pose == "slip":
        arm = math.sin(phase) * 10 * scale

        line(
            draw,
            [
                (x, shoulder_y),
                (x - 35 * scale, shoulder_y - 10 * scale),
                (x - 58 * scale, shoulder_y + 18 * scale + arm)
            ],
            BLACK,
            7 * scale
        )

        line(
            draw,
            [
                (x, shoulder_y),
                (x + 34 * scale, shoulder_y - 4 * scale),
                (x + 62 * scale, shoulder_y + 23 * scale - arm)
            ],
            BLACK,
            7 * scale
        )

        line(
            draw,
            [
                (x, hip_y),
                (x - 33 * scale, hip_y + 45 * scale),
                (x - 45 * scale, foot_y - 15 * scale)
            ],
            BLACK,
            8 * scale
        )

        line(
            draw,
            [
                (x, hip_y),
                (x + 35 * scale, hip_y + 40 * scale),
                (x + 47 * scale, foot_y - 5 * scale)
            ],
            BLACK,
            8 * scale
        )

    else:
        arm = math.sin(phase) * 24 * scale

        line(
            draw,
            [
                (x, shoulder_y),
                (x - 35 * scale + arm, shoulder_y + 45 * scale),
                (x - 48 * scale + arm, shoulder_y + 84 * scale)
            ],
            BLACK,
            7 * scale
        )

        line(
            draw,
            [
                (x, shoulder_y),
                (x + 35 * scale - arm, shoulder_y + 45 * scale),
                (x + 48 * scale - arm, shoulder_y + 84 * scale)
            ],
            BLACK,
            7 * scale
        )

        leg = math.sin(phase) * 22 * scale

        line(
            draw,
            [
                (x, hip_y),
                (x - 20 * scale - leg, hip_y + 58 * scale),
                (x - 30 * scale - leg, foot_y)
            ],
            BLACK,
            8 * scale
        )

        line(
            draw,
            [
                (x, hip_y),
                (x + 20 * scale + leg, hip_y + 58 * scale),
                (x + 30 * scale + leg, foot_y)
            ],
            BLACK,
            8 * scale
        )


def speech_strength(frame):
    start = int(1.0 * FPS)
    end = int(2.45 * FPS)

    if frame < start or frame > end:
        return 0.0

    t = (frame - start) / (end - start)

    value = (
        0.48
        + 0.32 * math.sin(t * 46)
        + 0.16 * math.sin(t * 83)
        + 0.08 * math.sin(t * 127)
    )

    fade = min(
        1.0,
        (t / 0.08),
        ((1.0 - t) / 0.08)
    )

    return clamp(value) * fade


def synthesize_audio():
    sample_rate = 22050
    total = int(DURATION * sample_rate)

    audio = np.zeros(
        total,
        dtype=np.float32
    )

    events = [
        (1.00, 1.55, 185, 0.20),
        (1.62, 2.45, 170, 0.22),
        (4.30, 4.65, 125, 0.12),
        (5.20, 5.65, 95, 0.10),
        (6.15, 6.65, 75, 0.08)
    ]

    for start, end, base, volume in events:
        a = int(start * sample_rate)
        b = int(end * sample_rate)

        if b <= a:
            continue

        n = b - a
        tt = np.arange(
            n,
            dtype=np.float32
        ) / sample_rate

        vibrato = 4.0 * np.sin(
            2 * np.pi * 4.0 * tt
        )

        carrier = (
            0.70 * np.sin(
                2 * np.pi * (base + vibrato) * tt
            )
            + 0.20 * np.sin(
                2 * np.pi * 2 * (base + vibrato) * tt
            )
            + 0.10 * np.sin(
                2 * np.pi * 3 * (base + vibrato) * tt
            )
        )

        syllables = (
            0.55
            + 0.45 * np.sin(
                2 * np.pi * 5.0 * tt
            )
        )

        attack = np.minimum(
            1.0,
            np.arange(n) / (
                sample_rate * 0.035
            )
        )

        release = np.minimum(
            1.0,
            np.arange(n, 0, -1) / (
                sample_rate * 0.055
            )
        )

        envelope = np.minimum(
            attack,
            release
        )

        audio[a:b] += (
            carrier
            * syllables
            * envelope
            * volume
        )

    rng = np.random.default_rng(12)

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


def render_background(draw):
    draw_tree(
        draw,
        960,
        570,
        1.0
    )

    rng = np.random.default_rng(123)

    for x in range(0, W, 20):
        h = int(rng.integers(5, 16))

        draw.line(
            (
                x,
                570,
                x + 3,
                570 - h
            ),
            fill=GROUND_DARK,
            width=2
        )

    draw_leaf_scatter(
        draw,
        rng,
        90
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

    for cx, cy, s in [
        (180, 130, 1.0),
        (470, 95, 0.75),
        (805, 165, 0.9)
    ]:
        for ox, oy, r in [
            (-42, 8, 31),
            (0, -12, 42),
            (43, 8, 31)
        ]:
            circle(
                draw,
                cx + ox * s,
                cy + oy * s,
                r * s,
                (248, 250, 251)
            )

    ground_y = 570

    draw.rectangle(
        (
            0,
            ground_y,
            W,
            H
        ),
        fill=GROUND
    )

    draw.line(
        (
            0,
            ground_y,
            W,
            ground_y
        ),
        fill=GROUND_DARK,
        width=7
    )

    render_background(draw)

    tree_x = 960

    if t < 0.16:
        phase = frame * 0.48

        stick_x = lerp(
            675,
            790,
            t / 0.16
        )

        foot_y = ground_y

        pose = "approach"

        look_x = tree_x - stick_x
        look_y = -100

        mouth = speech_strength(frame)

        tilt = 0.0

    elif t < 0.31:
        p = smooth(
            (t - 0.16) / 0.15
        )

        stick_x = lerp(
            790,
            835,
            p
        )

        foot_y = ground_y

        pose = "idle"

        look_x = tree_x - stick_x
        look_y = -130

        mouth = 0.0

        tilt = 0.035 * p

    elif t < 0.43:
        p = smooth(
            (t - 0.31) / 0.12
        )

        stick_x = 835

        foot_y = ground_y - 6 * p

        pose = "climb"

        look_x = tree_x - stick_x
        look_y = -150

        mouth = 0.0

        tilt = 0.055 * p

    elif t < 0.58:
        p = smooth(
            (t - 0.43) / 0.15
        )

        stick_x = 835

        climb_height = 105 * p

        foot_y = ground_y - climb_height

        pose = "climb"

        look_x = tree_x - stick_x
        look_y = -170

        mouth = 0.0

        tilt = 0.06

    elif t < 0.67:
        p = smooth(
            (t - 0.58) / 0.09
        )

        stick_x = 835

        slide = 95 * p

        foot_y = (
            ground_y
            - 105
            + slide
        )

        pose = "slip"

        look_x = 70
        look_y = 20

        mouth = 0.45 * p

        tilt = -0.10 * p

    elif t < 0.78:
        p = ease_out(
            (t - 0.67) / 0.11
        )

        stick_x = (
            835
            + 32 * p
        )

        foot_y = (
            ground_y
            - 10
            + 10 * p
        )

        pose = "slip"

        look_x = 55
        look_y = 15

        mouth = 0.75 * (1 - p)

        tilt = -0.10 * (1 - p)

    else:
        p = smooth(
            (t - 0.78) / 0.22
        )

        stick_x = lerp(
            867,
            850,
            p
        )

        foot_y = ground_y

        pose = "idle"

        look_x = tree_x - stick_x
        look_y = -120

        mouth = 0.0

        tilt = 0.0

    blink = (
        38 <= frame <= 41
        or 101 <= frame <= 104
        or 171 <= frame <= 174
        or 215 <= frame <= 218
    )

    draw_stickman(
        draw,
        stick_x,
        foot_y,
        scale=1.0,
        phase=frame * 0.48,
        pose=pose,
        look_x=look_x,
        look_y=look_y,
        mouth=mouth,
        blink=blink,
        tilt=tilt
    )

    if t > 0.80:
        p = smooth(
            (t - 0.80) / 0.20
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
    print("Rendering Scene 2...")

    for frame in range(FRAMES):
        render(frame)

    print("Generating audio...")
    synthesize_audio()

    print("Scene 2 complete.")
    print(f"Frames: {FRAME_DIR}")
    print(f"Audio:  {AUDIO_FILE}")


if __name__ == "__main__":
    main()
