"""FFmpeg-based video compression."""
import shutil
import subprocess
from pathlib import Path


def compress_video(
    input_path: Path,
    output_path: Path,
    crf: int = 28,
    preset: str = "medium",
    audio_bitrate: str = "128k",
) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError(
            "FFmpeg was not found. Install FFmpeg and ensure 'ffmpeg' is on PATH."
        )

    command = [
        ffmpeg,
        "-hide_banner",
        "-y",  # Output path was checked to not exist; this handles FFmpeg internals.
        "-i", str(input_path),
        "-c:v", "libx264",
        "-crf", str(crf),
        "-preset", preset,
        "-c:a", "aac",
        "-b:a", audio_bitrate,
        "-movflags", "+faststart",
        str(output_path),
    ]

    # Capture output to keep the terminal clean, but include FFmpeg's error detail on failure.
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        output_path.unlink(missing_ok=True)
        detail = result.stderr.strip().splitlines()
        useful_detail = "\n".join(detail[-12:]) if detail else "No FFmpeg details available."
        raise RuntimeError(f"FFmpeg compression failed:\n{useful_detail}")
