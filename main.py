"""Command-line entry point for the video compressor."""
import logging
import sys

from video_compressor.cli import parse_args
from video_compressor.compressor import compress_video
from video_compressor.file_manager import prepare_paths
from video_compressor.utils import format_bytes, configure_logging


def main() -> int:
    configure_logging()
    args = parse_args()

    try:
        input_path, output_path = prepare_paths(args.input, args.output)
        source_size = input_path.stat().st_size

        logging.info("Input: %s", input_path)
        logging.info("Output: %s", output_path)
        logging.info("Original size: %s", format_bytes(source_size))

        compress_video(
            input_path=input_path,
            output_path=output_path,
            crf=args.crf,
            preset=args.preset,
            audio_bitrate=args.audio_bitrate,
        )

        if not output_path.exists() or output_path.stat().st_size == 0:
            logging.error("Compression did not produce a valid output file.")
            return 1

        output_size = output_path.stat().st_size
        saved = source_size - output_size
        percent = (saved / source_size * 100) if source_size else 0

        logging.info("Compression completed successfully.")
        logging.info("Compressed video: %s", output_path)
        logging.info("Compressed size: %s", format_bytes(output_size))
        if saved >= 0:
            logging.info("Space saved: %s (%.1f%%)", format_bytes(saved), percent)
        else:
            logging.warning(
                "Output is %s larger than the original (%.1f%%).",
                format_bytes(-saved),
                abs(percent),
            )
        return 0
    except (FileNotFoundError, ValueError, RuntimeError, OSError) as exc:
        logging.error("%s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
