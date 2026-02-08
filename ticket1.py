import os

from src.main import run_extraction


def prompt_input(prompt_text, default=None):
    value = input(prompt_text).strip()
    return value if value else default


def main():
    print("\n🧠 MindFrame – Interactive Frame Extraction\n")

    video_path = prompt_input("Enter video path: ")
    while not video_path or not os.path.isfile(video_path):
        print("❌ Invalid video path. Please try again.")
        video_path = prompt_input("Enter video path: ")

    engine = prompt_input("Choose engine (ffmpeg/opencv) [ffmpeg]: ", "ffmpeg")
    while engine not in {"ffmpeg", "opencv"}:
        print("❌ Engine must be 'ffmpeg' or 'opencv'")
        engine = prompt_input("Choose engine (ffmpeg/opencv) [ffmpeg]: ", "ffmpeg")

    fps_input = prompt_input("Enter FPS (e.g., 1, 5, 10): ")
    while True:
        try:
            fps = float(fps_input)
            if fps <= 0:
                raise ValueError
            break
        except Exception:
            print("❌ FPS must be a positive number")
            fps_input = prompt_input("Enter FPS (e.g., 1, 5, 10): ")

    output_dir = prompt_input("Enter output directory [output]: ", "output")

    save_meta = prompt_input("Save metadata? (y/n) [y]: ", "y").lower() == "y"

    print("\n🚀 Starting extraction...\n")

    run_extraction(
        video_path=video_path,
        fps=fps,
        engine=engine,
        output_dir=output_dir,
        image_format="jpg",
        save_metadata=save_meta,
    )

    print("\n✅ Done. Check the output directory.\n")


if __name__ == "__main__":
    main()
