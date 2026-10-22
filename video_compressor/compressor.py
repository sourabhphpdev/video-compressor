
"""FFmpeg compression with real-time progress and motivational quotes."""

import random
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

from .motivational_q import MOTIVATIONAL_QUOTES


def get_video_duration(input_path: Path) -> float:
    """Return video duration in seconds using ffprobe."""
    ffprobe = shutil.which("ffprobe")

    if not ffprobe:
        raise RuntimeError(
            "ffprobe was not found. Install FFmpeg and ensure its bin "
            "directory is on PATH."
        )

    result = subprocess.run(
        [
            ffprobe,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(input_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Could not read video duration: {result.stderr.strip()}"
        )

    try:
        duration = float(result.stdout.strip())
    except ValueError as exc:
        raise RuntimeError("Could not determine video duration.") from exc

    if duration <= 0:
        raise RuntimeError("The input video has an invalid duration.")

    return duration


def format_time(seconds: float) -> str:
    """Format seconds as HH:MM:SS."""
    seconds = max(0, int(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{secs:02}"



def print_progress(
    percent: float,
    elapsed: float,
    video_time: float,
    quote: str | None = None,
) -> None:
    """Display progress and motivational quote on a single updating line."""
    width = 20
    filled = int(width * percent / 100)
    bar = "#" * filled + "-" * (width - filled)

    # Keep the current quote until a new one is selected.
    if quote:
        print_progress.current_quote = quote

    current_quote = getattr(
        print_progress,
        "current_quote",
        "Keep learning, keep building!"
    )

    line = (
        f"\r[{bar}] {percent:6.2f}%"
        f" | Video: {format_time(video_time)}"
        f" | Elapsed: {format_time(elapsed)}"
        f" | 💡 {current_quote}"
    )

    # Clear any leftover characters from a longer previous line.
    sys.stdout.write(line.ljust(print_progress.last_width))
    sys.stdout.flush()
    print_progress.last_width = len(line)


print_progress.last_width = 0



def compress_video(
    input_path: Path,
    output_path: Path,
    crf: int = 28,
    preset: str = "medium",
    audio_bitrate: str = "128k",
) -> None:
    """Compress a video and show percentage progress and quotes."""
    ffmpeg = shutil.which("ffmpeg")

    if not ffmpeg:
        raise RuntimeError(
            "FFmpeg was not found. Install FFmpeg and ensure it is on PATH."
        )

    duration = get_video_duration(input_path)

    command = [
        ffmpeg,
        "-hide_banner",
        "-nostats",
        "-i", str(input_path),
        "-c:v", "libx264",
        "-crf", str(crf),
        "-preset", preset,
        "-c:a", "aac",
        "-b:a", audio_bitrate,
        "-movflags", "+faststart",
        "-progress", "pipe:1",
        "-nostdin",
        str(output_path),
    ]

    start_time = time.monotonic()
    next_quote_time = start_time + 5
    last_quote = None
    error_lines = []

    # Drain stderr concurrently so FFmpeg cannot block on a full error pipe.
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    def read_stderr():
        if process.stderr:
            for line in process.stderr:
                error_lines.append(line.rstrip())

    stderr_thread = threading.Thread(target=read_stderr, daemon=True)
    stderr_thread.start()

    video_time = 0.0
    last_percent = 0.0

    try:
        if process.stdout is None:
            raise RuntimeError("Could not read FFmpeg progress output.")

        for line in process.stdout:
            line = line.strip()

            # FFmpeg emits machine-readable progress key/value pairs.
            if line.startswith("out_time="):
                timestamp = line.partition("=")[2]
                try:
                    hours, minutes, seconds = timestamp.split(":")
                    video_time = (
                        int(hours) * 3600
                        + int(minutes) * 60
                        + float(seconds)
                    )
                except (ValueError, TypeError):
                    pass

            elif line == "progress=continue" or line == "progress=end":
                now = time.monotonic()
                elapsed = now - start_time

                if line == "progress=end":
                    last_percent = 100.0
                    video_time = duration
                else:
                    last_percent = min(
                        99.9, max(0.0, video_time / duration * 100)
                    )

                quote = None
                if now >= next_quote_time and line != "progress=end":
                    choices = [
                        q for q in MOTIVATIONAL_QUOTES if q != last_quote
                    ]
                    quote = random.choice(choices)
                    last_quote = quote
                    next_quote_time = now + 5

                print_progress(
                    last_percent, elapsed, video_time, quote
                )

                if line == "progress=end":
                    print()

        return_code = process.wait()
        stderr_thread.join()

        if return_code != 0:
            output_path.unlink(missing_ok=True)
            detail = "\n".join(error_lines[-12:])
            raise RuntimeError(
                "FFmpeg compression failed:\n"
                + (detail or "No FFmpeg error details available.")
            )

        if not output_path.exists() or output_path.stat().st_size == 0:
            raise RuntimeError("FFmpeg finished without creating a valid output.")

        # Ensure the terminal displays completion after successful encoding.
        print_progress(100.0, time.monotonic() - start_time, duration)
        print("\nCompression completed successfully!")

    except BaseException:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        output_path.unlink(missing_ok=True)
        raise
    finally:
        if process.stdout:
            process.stdout.close()
        if process.stderr:
            process.stderr.close()
