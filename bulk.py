
import argparse
import tempfile
import time
from pathlib import Path

from video_compressor.compressor import compress_video


VIDEO_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".wmv",
    ".flv",
    ".webm",
    ".m4v",
    ".mpeg",
    ".mpg",
    ".3gp",
    ".ts",
}


def find_videos(input_folder: Path) -> list[Path]:
    """Find supported video files directly inside the input folder."""
    return sorted(
        (
            path
            for path in input_folder.iterdir()
            if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS
        ),
        key=lambda path: path.name.lower(),
    )


def create_temp_file(videos: list[Path]) -> Path:
    """Write the list of video paths to a temporary text file."""
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".txt",
        prefix="video_compressor_",
        delete=False,
    ) as temp_file:
        for video in videos:
            temp_file.write(f"{video}\n")

        return Path(temp_file.name)

def display_header()->None:
    """Redraw the status table in the terminal."""
    # Clear the terminal screen before drawing the updated table.
    print("\033[2J\033[H", end="")
    print("=" * 100)
    print("                       BULK VIDEO COMPRESSOR")
    print("=" * 100)
    # print(f"{'VIDEO NAME':<60} {'STATUS':<20}")
    # print("-" * 100)

def display_stats(videos: list[Path], statuses: dict[Path, str]) -> None:
    """Redraw the status table in the terminal."""
    # Clear the terminal screen before drawing the updated table.

    # for video in videos:
    #     status = statuses.get(video, "PENDING")
    #     print(f"{video.name[:58]:<60} {status:<20}")

    print("-" * 100)
    print(f"Total videos: {len(videos)}")
    print(f"Existing: {sum(s == 'EXIST' for s in statuses.values())}")
    print(f"Pending: {sum(s == 'PENDING' for s in statuses.values())}")
    print(f"Processing: {sum(s == 'PROCESSING' for s in statuses.values())}")
    print(f"Completed: {sum(s == 'COMPLETED' for s in statuses.values())}")
    print(f"Failed: {sum(s == 'FAILED' for s in statuses.values())}")
    print("=" * 100)
    print()

def display_status(videos: list[Path], statuses: dict[Path, str]) -> None:
    """Redraw the status table in the terminal."""
    # Clear the terminal screen before drawing the updated table.

    for video in videos:
        status = statuses.get(video, "PENDING")
        print(f"{video.name[:58]:<60} {status:<20}")

    print("-" * 100)
    print(f"Total videos: {len(videos)}")
    print(f"Existing: {sum(s == 'EXIST' for s in statuses.values())}")
    print(f"Pending: {sum(s == 'PENDING' for s in statuses.values())}")
    print(f"Processing: {sum(s == 'PROCESSING' for s in statuses.values())}")
    print(f"Completed: {sum(s == 'COMPLETED' for s in statuses.values())}")
    print(f"Failed: {sum(s == 'FAILED' for s in statuses.values())}")
    print("=" * 100)
    print()


def bulk_compress(
    input_folder: Path,
    output_folder: Path = Path("output"),
    crf: int = 28,
    preset: str = "medium",
    audio_bitrate: str = "128k",
) -> None:
    """Compress all eligible videos in a folder, skipping existing outputs."""
   
    display_header()

    if not input_folder.exists() or not input_folder.is_dir():
        raise ValueError(f"Input folder does not exist: {input_folder}")

    # output_folder.mkdir(parents=True, exist_ok=True)
    try:
        output_folder.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        print(f"Error: Insufficient permissions to create directory: {output_folder}")
    except FileExistsError:
        print(f"Error: A non-directory file already exists at this path: {output_folder}")
    except OSError as e:
        print(f"Error creating directory {output_folder}: {e}")

    videos = find_videos(input_folder)

    if not videos:
        print(f"No supported video files found in: {input_folder}")
        return

    # Create a temporary manifest containing every discovered video.
    temp_path = create_temp_file(videos)

    try:
        # Read the manifest so the processing list comes from the temp file.
        with temp_path.open("r", encoding="utf-8") as file:
            video_list = [Path(line.strip()) for line in file if line.strip()]

        statuses: dict[Path, str] = {}

        # Mark files that already have output as EXIST.
        for video in video_list:
            output_path = output_folder / video.name

            if output_path.exists():
                statuses[video] = "EXIST"
            else:
                statuses[video] = "PENDING"

        # display_status(video_list, statuses)

        for video in video_list:
            # Skip files already compressed.
            if statuses[video] == "EXIST":
                continue

            output_path = output_folder / video.name

            # Recheck before processing in case the output appeared meanwhile.
            if output_path.exists():
                statuses[video] = "EXIST"
                # display_status(video_list, statuses)
                continue

            statuses[video] = "PROCESSING"
            # display_status(video_list, statuses)

            print(f"Compressing: {video.name}")
            print(f"Output: {output_path}")
            print()

            try:
                compress_video(
                    input_path=video,
                    output_path=output_path,
                    crf=crf,
                    preset=preset,
                    audio_bitrate=audio_bitrate,
                )

                statuses[video] = (
                    "COMPLETED" if output_path.exists() else "FAILED"
                )

            except Exception as exc:
                statuses[video] = "FAILED"
                print(f"\nError compressing {video.name}: {exc}")
                time.sleep(1)

            # display_status(video_list, statuses)

        print("Bulk compression finished.")

    finally:
        # Always remove the temporary manifest when processing ends.
        temp_path.unlink(missing_ok=True)

    display_stats(video_list,statuses)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compress all videos in an input folder."
    )

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Folder containing the source videos.",
    )

    parser.add_argument(
        "-o",
        "--output",
        default="output",
        help="Output folder (default: output).",
    )

    parser.add_argument(
        "--crf",
        type=int,
        default=28,
        help="Video quality setting; lower values mean higher quality.",
    )

    parser.add_argument(
        "--preset",
        default="medium",
        choices=[
            "ultrafast",
            "superfast",
            "veryfast",
            "faster",
            "fast",
            "medium",
            "slow",
            "slower",
            "veryslow",
        ],
        help="FFmpeg encoding preset (default: medium).",
    )

    parser.add_argument(
        "--audio-bitrate",
        default="128k",
        help="Audio bitrate (default: 128k).",
    )

    args = parser.parse_args()

    try:
        bulk_compress(
            input_folder=Path(args.input),
            output_folder=Path(args.output),
            crf=args.crf,
            preset=args.preset,
            audio_bitrate=args.audio_bitrate,
        )
    except (ValueError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
