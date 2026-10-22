# Video Compressor

A small Python command-line application that compresses videos with FFmpeg and saves the result to an output directory.

## Requirements

- Python 3.10 or newer
- FFmpeg installed and available on your system `PATH`

No third-party Python packages are required.

### Install FFmpeg

- **Windows:** Install an FFmpeg build and add its `bin` directory to your `PATH`.
- **macOS:** `brew install ffmpeg`
- **Ubuntu/Debian:** `sudo apt update && sudo apt install ffmpeg`

Verify the installation:

```bash
ffmpeg -version
python --version
```

## Project structure

```text
video_compressor/
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
├── output/
│   └── .gitkeep
└── video_compressor/
    ├── __init__.py
    ├── cli.py
    ├── compressor.py
    ├── file_manager.py
    └── utils.py
```

## Usage

From the project root:

```bash
python main.py --input videos/sample.mp4
```

The compressed video is saved to `output/sample_compressed.mp4` by default.

Choose a custom output directory:

```bash
python main.py --input videos/sample.mp4 --output compressed_videos
```

Optional quality/speed settings:

```bash
python main.py -i videos/sample.mp4 -o output --crf 26 --preset medium --audio-bitrate 128k
```

- `--crf`: H.264 quality setting from 0 to 51. Lower values preserve more quality and usually create larger files. `28` is the default.
- `--preset`: Encoding speed/compression trade-off. `medium` is the default.
- `--audio-bitrate`: AAC audio bitrate, default `128k`.

The source video is not modified. The app writes an MP4 output using H.264 video and AAC audio. Some source formats/codecs may not be supported by the selected output settings.

## Notes

- Existing output files are not overwritten; choose another folder or move the existing output file.
- Compression may not always reduce file size. Results depend on source codec, quality, resolution, and bitrate.
- If FFmpeg is missing, install it and ensure `ffmpeg` is available on `PATH`.
