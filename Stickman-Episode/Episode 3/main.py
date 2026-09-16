import os
import shutil
import subprocess
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))

SCENES = [
    (1, "scene1.py", "scene1_frames", "scene1_audio.wav"),
    (2, "scene2.py", "scene2_frames", "scene2_audio.wav"),
    (3, "scene3.py", "scene3_frames", "scene3_audio.wav"),
    (4, "scene4.py", "scene4_frames", "scene4_audio.wav"),
    (5, "scene5.py", "scene5_frames", "scene5_audio.wav"),
    (6, "scene6.py", "scene6_frames", "scene6_audio.wav"),
]

TEMP_DIR = os.path.join(
    ROOT,
    "_video_temp"
)

OUTPUT = os.path.join(
    ROOT,
    "stickman_tree.mp4"
)


def run_scene(number, script):
    print(f"Rendering Scene {number}...")

    subprocess.run(
        [
            sys.executable,
            script
        ],
        cwd=ROOT,
        check=True
    )

    print(f"Scene {number} rendered successfully.")


def check_scene_files():
    for number, script, frame_dir, audio_file in SCENES:
        script_path = os.path.join(
            ROOT,
            script
        )

        frames_path = os.path.join(
            ROOT,
            frame_dir
        )

        audio_path = os.path.join(
            ROOT,
            audio_file
        )

        if not os.path.isfile(script_path):
            raise FileNotFoundError(
                f"Scene {number} script not found: {script}"
            )

        if not os.path.isdir(frames_path):
            raise FileNotFoundError(
                f"Scene {number} frames not found: {frame_dir}"
            )

        if not os.path.isfile(audio_path):
            raise FileNotFoundError(
                f"Scene {number} audio not found: {audio_file}"
            )


def create_scene_video(
    number,
    frame_dir,
    audio_file
):
    os.makedirs(
        TEMP_DIR,
        exist_ok=True
    )

    output = os.path.join(
        TEMP_DIR,
        f"scene{number}.mp4"
    )

    frames = os.path.join(
        ROOT,
        frame_dir,
        "frame_%04d.png"
    )

    audio = os.path.join(
        ROOT,
        audio_file
    )

    command = [
        "ffmpeg",
        "-y",
        "-framerate",
        "30",
        "-i",
        frames,
        "-i",
        audio,
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        output
    ]

    subprocess.run(
        command,
        check=True
    )

    return output


def concatenate_videos(videos):
    concat_file = os.path.join(
        TEMP_DIR,
        "concat.txt"
    )

    with open(
        concat_file,
        "w",
        encoding="utf-8"
    ) as file:
        for video in videos:
            path = os.path.abspath(video)
            path = path.replace("\\", "/")

            file.write(
                f"file '{path}'\n"
            )

    command = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        concat_file,
        "-c",
        "copy",
        OUTPUT
    ]

    subprocess.run(
        command,
        check=True
    )


def cleanup():
    if os.path.isdir(TEMP_DIR):
        shutil.rmtree(
            TEMP_DIR
        )


def main():
    print("StickMan Tree Video")
    print()

    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "FFmpeg is required but was not found."
        )

    for number, script, _, _ in SCENES:
        run_scene(
            number,
            script
        )

    print()
    print("Checking rendered scenes...")

    check_scene_files()

    print()
    print("Encoding scenes...")

    videos = []

    for number, _, frame_dir, audio_file in SCENES:
        video = create_scene_video(
            number,
            frame_dir,
            audio_file
        )

        videos.append(video)

    print()
    print("Joining all scenes...")

    concatenate_videos(
        videos
    )

    cleanup()

    print()
    print("StickMan Episode 3 complete.")
    print(f"Output: {OUTPUT}")


if __name__ == "__main__":
    main()
