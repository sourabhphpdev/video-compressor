"""Input/output path validation and preparation."""
from pathlib import Path


def prepare_paths(input_value: str, output_dir_value: str):
    input_path = Path(input_value).expanduser()

    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")
    if not input_path.is_file():
        raise ValueError(f"Input path is not a file: {input_path}")

    output_dir = Path(output_dir_value).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Encode to MP4 for a predictable H.264/AAC output container.
    output_path = output_dir / f"{input_path.stem}_compressed.mp4"

    if input_path.resolve() == output_path.resolve():
        raise ValueError("Input and output paths must be different.")
    if output_path.exists():
        raise FileExistsError(
            f"Output file already exists: {output_path}. "
            "Move/delete it or choose another output directory."
        )

    return input_path.resolve(), output_path.resolve()
