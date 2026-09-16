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
FRAME_DIR = os.path.join(ROOT, "scene4_frames")
AUDIO_FILE = os.path.join(ROOT, "scene4_audio.wav")

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

    rng = np.random.default_rng(917)

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

    for _ in range(110):
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
    pose="idle",
    phase=0.0,
    look_x=0.0,
    look_y=0.0,
    mouth=0.0,
    blink=False,
    lean=0.0,
    compression=0.0,
    climb_cycle=0.0
):
    head_r = 29 * scale

    body_length = (
        145
        * scale
        * (1.0 - 0.10 * compression)
    )

    neck_y = foot_y - body_length
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

    if pose == "pro":
        brow_y = head_y - 19 * scale

        line(
            draw,
            [
                (head_x - 19 * scale, brow_y - 2 * scale),
                (head_x - 7 * scale, brow_y + 2 * scale)
            ],
            BLACK,
            3 * scale
        )

        line(
            draw,
            [
                (head_x + 7 * scale, brow_y + 2 * scale),
                (head_x + 19 * scale, brow_y - 2 * scale)
            ],
            BLACK,
            3 * scale
        )

    elif pose == "shock":
        line(
            draw,
            [
                (head_x - 19 * scale, head_y - 19 * scale),
                (head_x - 7 * scale, head_y - 14 * scale)
            ],
            BLACK,
            3 * scale
        )

        line(
            draw,
            [
                (head_x + 7 * scale, head_y - 14 * scale),
                (head_x + 19 * scale, head_y - 19 * scale)
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

    if pose == "stretch":
        line(
            draw,
            [
                (x, shoulder_y),
                (x - 35 * scale, shoulder_y - 55 * scale),
                (x - 40 * scale, shoulder_y - 88 * scale)
            ],
            BLACK,
            7 * scale
        )

        line(
            draw,
            [
                (x, shoulder_y),
                (x + 35 * scale, shoulder_y - 55 * scale),
                (x + 40 * scale, shoulder_y - 88 * scale)
            ],
            BLACK,
            7 * scale
        )

        line(
            draw,
            [
                (x, hip_y),
                (x - 30 * scale, hip_y + 50 * scale),
                (x - 35 * scale, foot_y)
            ],
            BLACK,
            8 * scale
        )

        line(
            draw,
            [
                (x, hip_y),
                (x + 30 * scale, hip_y + 50 * scale),
                (x + 35 * scale, foot_y)
            ],
            BLACK,
            8 * scale
        )

    elif pose == "pro":
        cycle = climb_cycle * math.pi * 2

        hand_wave = math.sin(cycle)
        leg_wave = math.sin(cycle + math.pi)

        left_hand_x = x - 44 * scale
        left_hand_y = (
            shoulder_y
            - 58 * scale
            - hand_wave * 15 * scale
        )

        right_hand_x = x + 44 * scale
        right_hand_y = (
            shoulder_y
            - 58 * scale
            + hand_wave * 15 * scale
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

        left_knee = (
            x - 29 * scale,
            hip_y + 28 * scale
        )

        right_knee = (
            x + 29 * scale,
            hip_y + 28 * scale
        )

        line(
            draw,
            [
                (x, hip_y),
                left_knee,
                (
                    x - 42 * scale,
                    foot_y - 18 * scale
                    - leg_wave * 12 * scale
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
                    x + 42 * scale,
                    foot_y - 35 * scale
                    + leg_wave * 12 * scale
                )
            ],
            BLACK,
            8 * scale
        )

    elif pose == "shock":
        arm = math.sin(phase) * 10 * scale

        line(
            draw,
            [
                (x, shoulder_y),
                (
                    x - 38 * scale,
                    shoulder_y - 22 * scale
                ),
                (
                    x - 65 * scale,
                    shoulder_y - 55 * scale + arm
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
                    shoulder_y - 22 * scale
                ),
                (
                    x + 65 * scale,
                    shoulder_y - 55 * scale - arm
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
                    x - 25 * scale,
                    hip_y + 58 * scale
                ),
                (
                    x - 32 * scale,
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
                    x + 25 * scale,
                    hip_y + 58 * scale
                ),
                (
                    x + 32 * scale,
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


def speech_strength(frame):
    start = int(0.55 * FPS)
    end = int(2.0 * FPS)

    if frame < start or frame > end:
        return 0.0

    t = (frame - start) / (end - start)

    signal = (
        0.50
        + 0.32 * math.sin(t * 43)
        + 0.15 * math.sin(t * 81)
        + 0.08 * math.sin(t * 127)
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
        (0.55, 1.10, 185, 0.18),
        (1.15, 2.00, 165, 0.22),

        (3.65, 3.82, 120, 0.08),
        (3.92, 4.12, 140, 0.09),
        (4.20, 4.40, 155, 0.10),

        (4.55, 5.05, 125, 0.10),
        (5.10, 5.65, 115, 0.11),
        (5.70, 6.25, 105, 0.12),
        (6.30, 6.85, 95, 0.12)
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
                / (sample_rate * 0.045)
            )
        )

        pulse = (
            0.55
            + 0.45
            * np.sin(
                2 * np.pi * 5.2 * tt
            )
        )

        audio[a:b] += (
            carrier
            * pulse
            * envelope
            * volume
        )

    rng = np.random.default_rng(91)

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

    draw_tree(
        draw,
        tree_x,
        ground_y
    )

    if t < 0.12:
        p = smooth(t / 0.12)

        x = lerp(
            850,
            800,
            p
        )

        foot_y = ground_y

        pose = "idle"

        look_x = tree_x - x
        look_y = -100

        lean = 0.0
        compression = 0.0

    elif t < 0.25:
        p = smooth(
            (t - 0.12) / 0.13
        )

        x = 800

        foot_y = ground_y

        pose = "stretch"

        look_x = 150
        look_y = -140

        lean = 0.0
        compression = 0.0

    elif t < 0.34:
        p = smooth(
            (t - 0.25) / 0.09
        )

        x = lerp(
            800,
            850,
            p
        )

        foot_y = ground_y

        pose = "pro"

        look_x = tree_x - x
        look_y = -140

        lean = 0.0
        compression = 0.18 * (1 - p)

    elif t < 0.72:
        p = smooth(
            (t - 0.34) / 0.38
        )

        climb_height = 275 * p

        x = 850

        foot_y = ground_y - climb_height

        pose = "pro"

        look_x = tree_x - x
        look_y = -165

        lean = 0.02 * math.sin(p * math.pi * 5)

        compression = (
            0.08
            + 0.08 * abs(
                math.sin(p * math.pi * 7)
            )
        )

    elif t < 0.82:
        p = smooth(
            (t - 0.72) / 0.10
        )

        x = 850

        foot_y = ground_y - 275

        pose = "pro"

        look_x = tree_x - x
        look_y = -215

        lean = -0.04 * p
        compression = 0.0

    else:
        p = smooth(
            (t - 0.82) / 0.18
        )

        x = 850

        foot_y = ground_y - 275

        pose = "shock"

        look_x = 90
        look_y = -150

        lean = 0.0
        compression = 0.0

    blink = (
        25 <= frame <= 28
        or 76 <= frame <= 79
        or 142 <= frame <= 145
        or 201 <= frame <= 204
    )

    if t < 0.34:
        climb_cycle = 0.0
    else:
        climb_cycle = (
            (t - 0.34) / 0.38
            * 4.8
        )

    mouth = speech_strength(frame)

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
        compression=compression,
        climb_cycle=climb_cycle
    )

    if t > 0.30:
        camera_progress = smooth(
            (t - 0.30) / 0.52
        )

        zoom = 1.0 + 0.045 * camera_progress

        vertical_shift = int(
            65 * camera_progress
        )

        crop_w = int(W / zoom)
        crop_h = int(H / zoom)

        left = (W - crop_w) // 2
        top = max(
            0,
            (H - crop_h) // 2
            - vertical_shift
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
    print("Rendering Scene 4...")

    for frame in range(FRAMES):
        render(frame)

    print("Generating audio...")
    synthesize_audio()

    print("Scene 4 complete.")
    print(f"Frames: {FRAME_DIR}")
    print(f"Audio: {AUDIO_FILE}")


if __name__ == "__main__":
    main()
