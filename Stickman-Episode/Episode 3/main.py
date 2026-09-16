import os
import shutil
import subprocess

import scene1
import scene2
import scene3
import scene4
import scene5
import scene6


ROOT = os.path.dirname(os.path.abspath(__file__))

SCENES = [
    (scene1, "scene1_frames", "scene1_audio.wav"),
    (scene2, "scene2_frames", "scene2_audio.wav"),
    (scene3, "scene3_frames", "scene3_audio.wav"),
    (scene4, "scene4_frames", "scene4_audio.wav"),
    (scene5, "scene5_frames", "scene5_audio.wav"),
    (scene6, "scene6_frames", "scene6_audio.wav")
]

OUTPUT = os.path.join(
    ROOT,
    "stickman_tree.mp4"
)

TEMP_DIR = os.path.join(
    ROOT,
    "_video_temp"
)


def run_scene(module, number):
    print(f"Rendering Scene {number}...")

    module.main()

    frame_dir = os.path.join(
        ROOT,
        f"scene{number}_frames"
    )

    audio_file = os.path.join(
        ROOT,
        f"scene{number}_audio.wav"
    )

    if not os.path.isdir(frame_dir):
        raise RuntimeError(
            f"Scene {number} did not create its frame directory."
        )

    if not os.path.isfile(audio_file):
        raise RuntimeError(
            f"Scene {number} did not create its audio file."
        )

    return frame_dir, audio_file


def check_ffmpeg():
    return shutil.which("ffmpeg") is not None


def create_scene_video(
    scene_number,
    frame_dir,
    audio_file
):
    output = os.path.join(
        TEMP_DIR,
        f"scene{scene_number}.mp4"
    )

    os.makedirs(
        TEMP_DIR,
        exist_ok=True
    )

    pattern = os.path.join(
        frame_dir,
        "frame_%04d.png"
    )

    command = [
        "ffmpeg",
        "-y",
        "-framerate",
        "30",
        "-i",
        pattern,
        "-i",
        audio_file,
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


def concatenate_videos(video_files):
    concat_file = os.path.join(
        TEMP_DIR,
        "concat.txt"
    )

    with open(
        concat_file,
        "w",
        encoding="utf-8"
    ) as file:
        for video in video_files:
            path = os.path.abspath(video)

            file.write(
                f"file '{path.replace(chr(92), '/')}'\n"
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
            TEMP_DIR,
            ignore_errors=True
        )


def main():
    print("StickMan Tree Video")
    print()

    if not check_ffmpeg():
        print(
            "FFmpeg was not found."
        )
        print(
            "The six scenes can still be rendered,"
        )
        print(
            "but an MP4 cannot be assembled until FFmpeg is installed."
        )
        print()

    scene_files = []

    for number, (module, _, _) in enumerate(
        SCENES,
        start=1
    ):
        frame_dir, audio_file = run_scene(
            module,
            number
        )

        scene_files.append(
            (
                number,
                frame_dir,
                audio_file
            )
        )

    if not check_ffmpeg():
        print()
        print("All 6 scenes rendered successfully.")
        return

    print()
    print("Encoding scenes...")

    videos = []

    for number, frame_dir, audio_file in scene_files:
        video = create_scene_video(
            number,
            frame_dir,
            audio_file
        )

        videos.append(video)

    print()
    print("Joining scenes...")

    concatenate_videos(videos)

    cleanup()

    print()
    print("Video complete.")
    print(f"Output: {OUTPUT}")


if __name__ == "__main__":
    main()
