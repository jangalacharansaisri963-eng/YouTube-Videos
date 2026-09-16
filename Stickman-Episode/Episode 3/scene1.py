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
FRAME_DIR = os.path.join(ROOT, "scene1_frames")
AUDIO_FILE = os.path.join(ROOT, "scene1_audio.wav")

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


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def smooth(x):
    x = clamp(x)
    return x * x * (3.0 - 2.0 * x)


def lerp(a, b, t):
    return a + (b - a) * smooth(t)


def circle(draw, x, y, r, fill, outline=None, width=1):
    draw.ellipse(
        (
            int(x-r),
            int(y-r),
            int(x+r),
            int(y+r)
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
            int(x-trunk_w/2),
            int(trunk_top),
            int(x+trunk_w/2),
            int(ground_y)
        ),
        radius=int(22*scale),
        fill=TRUNK
    )

    line(
        draw,
        [
            (x-5*scale, ground_y),
            (x-3*scale, trunk_top+95*scale),
            (x-112*scale, trunk_top-5*scale)
        ],
        TRUNK_DARK,
        17*scale
    )

    line(
        draw,
        [
            (x+5*scale, trunk_top+145*scale),
            (x+112*scale, trunk_top+8*scale)
        ],
        TRUNK_DARK,
        16*scale
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
            x+ox*scale,
            trunk_top+oy*scale,
            r*scale,
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
            x+ox*scale,
            trunk_top+oy*scale,
            r*scale,
            LEAF
        )


def draw_stickman(
    draw,
    x,
    foot_y,
    scale=1.0,
    phase=0.0,
    mouth=0.0,
    blink=False,
    look_x=0.0,
    look_y=0.0,
    head_turn=0.0,
    excited=False
):
    head_r = 29 * scale

    neck_y = foot_y - 145 * scale
    head_y = neck_y - 38 * scale
    shoulder_y = neck_y + 12 * scale
    hip_y = foot_y - 65 * scale

    # Ground shadow
    draw.ellipse(
        (
            int(x-48*scale),
            int(foot_y+2),
            int(x+48*scale),
            int(foot_y+15*scale)
        ),
        fill=(57, 108, 50)
    )

    # Head follows body rotation slightly.
    head_x = x + head_turn * 8 * scale

    circle(
        draw,
        head_x,
        head_y,
        head_r,
        WHITE,
        BLACK,
        6*scale
    )

    # Eye direction is now calculated from the target.
    eye_y = head_y - 3 * scale

    target_x = head_x + look_x
    target_y = eye_y + look_y

    dx = target_x - head_x
    dy = target_y - eye_y
    distance = max(1.0, math.hypot(dx, dy))

    max_eye = 5.5 * scale

    eye_dx = clamp(dx/distance, -1, 1) * max_eye
    eye_dy = clamp(dy/distance, -1, 1) * max_eye

    if blink:
        line(
            draw,
            [
                (head_x-17*scale, eye_y),
                (head_x-7*scale, eye_y)
            ],
            BLACK,
            3*scale
        )

        line(
            draw,
            [
                (head_x+7*scale, eye_y),
                (head_x+17*scale, eye_y)
            ],
            BLACK,
            3*scale
        )
    else:
        for ex in (-12, 12):
            circle(
                draw,
                head_x+ex*scale,
                eye_y,
                4*scale,
                BLACK
            )

            circle(
                draw,
                head_x+ex*scale+eye_dx,
                eye_y+eye_dy,
                1.7*scale,
                WHITE
            )

    # Eyebrows
    brow_offset = -3 if excited else 0

    line(
        draw,
        [
            (head_x-19*scale, head_y-16*scale+brow_offset),
            (head_x-7*scale, head_y-20*scale+brow_offset)
        ],
        BLACK,
        3*scale
    )

    line(
        draw,
        [
            (head_x+7*scale, head_y-20*scale+brow_offset),
            (head_x+19*scale, head_y-16*scale+brow_offset)
        ],
        BLACK,
        3*scale
    )

    # Animated mouth.
    mouth_y = head_y + 15*scale

    if mouth > 0.72:
        draw.ellipse(
            (
                int(head_x-12*scale),
                int(mouth_y-5*scale),
                int(head_x+12*scale),
                int(mouth_y+15*scale)
            ),
            fill=BLACK
        )

    elif mouth > 0.40:
        draw.ellipse(
            (
                int(head_x-10*scale),
                int(mouth_y),
                int(head_x+10*scale),
                int(mouth_y+10*scale)
            ),
            fill=BLACK
        )

    elif mouth > 0.10:
        line(
            draw,
            [
                (head_x-8*scale, mouth_y+2*scale),
                (head_x+8*scale, mouth_y+2*scale)
            ],
            BLACK,
            4*scale
        )

    else:
        line(
            draw,
            [
                (head_x-7*scale, mouth_y+2*scale),
                (head_x+7*scale, mouth_y+2*scale)
            ],
            BLACK,
            3*scale
        )

    # Body
    line(
        draw,
        [
            (x, neck_y),
            (x, hip_y)
        ],
        BLACK,
        8*scale
    )

    # Arm movement
    if excited:
        line(
            draw,
            [
                (x, shoulder_y),
                (x-38*scale, shoulder_y-42*scale),
                (x-60*scale, shoulder_y-82*scale)
            ],
            BLACK,
            7*scale
        )

        line(
            draw,
            [
                (x, shoulder_y),
                (x+38*scale, shoulder_y-42*scale),
                (x+60*scale, shoulder_y-82*scale)
            ],
            BLACK,
            7*scale
        )
    else:
        arm = math.sin(phase) * 24 * scale

        line(
            draw,
            [
                (x, shoulder_y),
                (x-35*scale+arm, shoulder_y+45*scale),
                (x-48*scale+arm, shoulder_y+84*scale)
            ],
            BLACK,
            7*scale
        )

        line(
            draw,
            [
                (x, shoulder_y),
                (x+35*scale-arm, shoulder_y+45*scale),
                (x+48*scale-arm, shoulder_y+84*scale)
            ],
            BLACK,
            7*scale
        )

    # Legs
    leg = math.sin(phase) * 22 * scale

    line(
        draw,
        [
            (x, hip_y),
            (x-20*scale-leg, hip_y+58*scale),
            (x-30*scale-leg, foot_y)
        ],
        BLACK,
        8*scale
    )

    line(
        draw,
        [
            (x, hip_y),
            (x+20*scale+leg, hip_y+58*scale),
            (x+30*scale+leg, foot_y)
        ],
        BLACK,
        8*scale
    )


def speech_strength(frame):
    """
    Returns a natural-looking mouth opening value.
    Dialogue is divided into phoneme-like pulses instead
    of simply opening the mouth once.
    """

    if frame < int(FRAMES*0.45):
        return 0.0

    if frame < int(FRAMES*0.58):
        t = (frame-FRAMES*0.45)/(FRAMES*0.13)

    elif frame < int(FRAMES*0.76):
        t = (frame-FRAMES*0.58)/(FRAMES*0.18)

    elif frame < int(FRAMES*0.96):
        t = (frame-FRAMES*0.76)/(FRAMES*0.20)

    else:
        return 0.0

    value = (
        0.5
        + 0.34*math.sin(t*42)
        + 0.16*math.sin(t*77)
        + 0.08*math.sin(t*113)
    )

    return clamp(value)


def synthesize_voice():
    """
    Creates a simple synthetic voice WAV.

    This is intentionally generated offline with Python's
    standard library, so no TTS package is required.
    """

    sample_rate = 22050
    total = int(DURATION * sample_rate)

    audio = np.zeros(total, dtype=np.float32)

    phrases = [
        (3.55, 4.15, 205, 0.22),
        (4.75, 5.95, 185, 0.24),
        (6.15, 7.65, 170, 0.25)
    ]

    for start, end, base, volume in phrases:
        a = int(start*sample_rate)
        b = int(end*sample_rate)

        if b <= a:
            continue

        n = b-a
        tt = np.arange(n, dtype=np.float32)/sample_rate

        syllable = (
            0.55
            + 0.45*np.sin(2*np.pi*5.2*tt)
        )

        vibrato = 5*np.sin(2*np.pi*4.5*tt)

        carrier = (
            0.70*np.sin(
                2*np.pi*(base+vibrato)*tt
            )
            + 0.20*np.sin(
                2*np.pi*2*(base+vibrato)*tt
            )
            + 0.10*np.sin(
                2*np.pi*3*(base+vibrato)*tt
            )
        )

        envelope = np.minimum(
            1,
            np.minimum(
                np.arange(n)/(
                    sample_rate*0.04
                ),
                np.arange(n, 0, -1)/(
                    sample_rate*0.05
                )
            )
        )

        audio[a:b] += (
            carrier
            * syllable
            * envelope
            * volume
        )

    # Very soft outdoor ambience.
    rng = np.random.default_rng(7)
    noise = rng.normal(
        0,
        0.003,
        total
    ).astype(np.float32)

    audio += noise

    audio = np.clip(audio, -1, 1)

    pcm = (audio*32767).astype(np.int16)

    with wave.open(AUDIO_FILE, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(pcm.tobytes())


def render(frame):
    t = frame/(FRAMES-1)

    # Sky
    y = np.arange(H, dtype=np.float32)[:, None]
    q = y/H

    gradient = (
        SKY_TOP*(1-q[..., None])
        + SKY_BOTTOM*q[..., None]
    )

    arr = np.broadcast_to(
        gradient,
        (H, W, 3)
    ).copy()

    img = Image.fromarray(
        np.clip(arr, 0, 255).astype(np.uint8),
        "RGB"
    )

    draw = ImageDraw.Draw(img)

    # Sun
    circle(
        draw,
        1080,
        105,
        58,
        (255, 226, 135)
    )

    # Clouds
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
                cx+ox*s,
                cy+oy*s,
                r*s,
                (248, 250, 251)
            )

    # Ground
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

    # Grass
    rng = np.random.default_rng(123)

    for x in range(0, W, 20):
        h = int(rng.integers(5, 16))

        draw.line(
            (x, ground_y, x+3, ground_y-h),
            fill=GROUND_DARK,
            width=2
        )

    # Tree
    tree_x = 960
    draw_tree(draw, tree_x, ground_y)

    # Character movement
    walk_end = int(FRAMES*0.43)

    if frame < walk_end:
        p = smooth(frame/walk_end)

        stick_x = lerp(170, 675, p)

        bounce = abs(
            math.sin(frame*0.45)
        )*4

        foot_y = ground_y-bounce
        phase = frame*0.48

        # Look forward while walking.
        look_x = 0
        look_y = 0
        head_turn = 0
        excited = False

    else:
        # Small body reaction after stopping.
        p = smooth(
            (frame-walk_end)
            /max(1, FRAMES-walk_end)
        )

        stick_x = 675 + math.sin(p*math.pi)*4
        foot_y = ground_y
        phase = 0

        # Tree is to the RIGHT and slightly ABOVE
        # the character's eyes.
        target_x = tree_x-stick_x
        target_y = 350-425

        look_x = target_x
        look_y = target_y

        # Head gradually turns toward tree.
        head_turn = smooth(
            clamp((t-0.47)/0.16)
        )

        excited = t > 0.78

    mouth = speech_strength(frame)

    # Blink naturally, but don't blink while mouth is
    # doing the strongest part of the first reaction.
    blink = (
        68 <= frame <= 72
        or 126 <= frame <= 130
        or 188 <= frame <= 192
    )

    draw_stickman(
        draw,
        stick_x,
        foot_y,
        scale=1.0,
        phase=phase,
        mouth=mouth,
        blink=blink,
        look_x=look_x,
        look_y=look_y,
        head_turn=head_turn,
        excited=excited
    )

    # Slight cinematic push-in after noticing the tree.
    if t > 0.76:
        z = 1 + 0.035*smooth(
            (t-0.76)/0.24
        )

        nw = int(W/z)
        nh = int(H/z)

        left = (W-nw)//2
        top = (H-nh)//2

        img = img.crop(
            (
                left,
                top,
                left+nw,
                top+nh
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


if __name__ == "__main__":
    print("Rendering Scene 1...")

    for frame in range(FRAMES):
        render(frame)

    print("Generating audio...")
    synthesize_voice()

    print("Scene 1 complete.")
    print(f"Frames: {FRAME_DIR}")
    print(f"Audio:  {AUDIO_FILE}")
