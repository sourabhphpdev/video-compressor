"""Command-line argument parsing."""
import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compress a video file and save it to an output directory."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Path to the source video file."
    )
    parser.add_argument(
        "-o", "--output", default="output",
        help="Output directory (default: output)."
    )
    parser.add_argument(
        "--crf", type=int, default=28,
        help="H.264 quality setting from 0 to 51; lower means higher quality (default: 28)."
    )
    parser.add_argument(
        "--preset", choices=[
            "ultrafast", "superfast", "veryfast", "faster", "fast",
            "medium", "slow", "slower", "veryslow"
        ],
        default="medium",
        help="FFmpeg encoding speed/compression preset (default: medium)."
    )
    parser.add_argument(
        "--audio-bitrate", default="128k",
        help="AAC audio bitrate, e.g. 96k or 128k (default: 128k)."
    )
    args = parser.parse_args()

    if not 0 <= args.crf <= 51:
        parser.error("--crf must be between 0 and 51.")
    return args
