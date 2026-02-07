import argparse
import os
import sys


def parse_args():
    parser = argparse.ArgumentParser(
        description="InsightLens - Video Frame Extraction Module"
    )

    parser.add_argument(
        "--video",
        type=str,
        required=True,
        help="Path to input video file (mp4, avi, mov)"
    )

    parser.add_argument(
        "--fps",
        type=float,
        required=True,
        help="Frames per second to extract (e.g., 1, 5, 10)"
    )

    parser.add_argument(
        "--engine",
        type=str,
        choices=["ffmpeg", "opencv"],
        default="ffmpeg",
        help="Frame extraction engine (default: ffmpeg)"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="output",
        help="Output directory (default: ./output)"
    )

    parser.add_argument(
        "--image-format",
        type=str,
        choices=["jpg", "png"],
        default="jpg",
        help="Output image format (jpg or png)"
    )

    parser.add_argument(
        "--save-metadata",
        action="store_true",
        help="Save metadata.json with timestamps"
    )

    return parser.parse_args()


def validate_args(args):
    # Video file validation
    if not os.path.isfile(args.video):
        print(f"[ERROR] Video file not found: {args.video}")
        sys.exit(1)

    # FPS validation
    if args.fps <= 0:
        print("[ERROR] FPS must be greater than 0")
        sys.exit(1)

    # Output directory
    try:
        os.makedirs(args.output, exist_ok=True)
    except Exception as e:
        print(f"[ERROR] Cannot create output directory: {e}")
        sys.exit(1)


def main():
    args = parse_args()
    validate_args(args)

    # Lazy import to keep CLI lightweight
    from .main import run_extraction

    run_extraction(
        video_path=args.video,
        fps=args.fps,
        engine=args.engine,
        output_dir=args.output,
        image_format=args.image_format,
        save_metadata=args.save_metadata
    )


if __name__ == "__main__":
    main()
