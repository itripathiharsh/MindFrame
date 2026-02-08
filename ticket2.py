import os

from src.change_detection.runner import ChangeDetectionRunner


def prompt_input(prompt_text, default=None):
    value = input(prompt_text).strip()
    return value if value else default


def main():
    print("\n🧠 MindFrame – Interactive Change Detection (Ticket-2)\n")

    # Input directory (Ticket-1 output)
    input_dir = prompt_input(
        "Enter extraction output directory [outputs/extraction]: ",
        "outputs/extraction"
    )

    while not os.path.isdir(input_dir):
        print("❌ Invalid input directory. Please try again.")
        input_dir = prompt_input(
            "Enter extraction output directory [outputs/extraction]: ",
            "outputs/extraction"
        )

    images_dir = os.path.join(input_dir, "images")
    metadata_path = os.path.join(input_dir, "metadata.json")

    if not os.path.isdir(images_dir) or not os.path.isfile(metadata_path):
        print("❌ Input directory must contain 'images/' and 'metadata.json'")
        return

    # Output directory
    output_dir = prompt_input(
        "Enter output directory [outputs/change_detection]: ",
        "outputs/change_detection"
    )

    # Change detection method
    method = prompt_input(
        "Choose method (ssim/mse) [ssim]: ",
        "ssim"
    ).lower()

    while method not in {"ssim", "mse"}:
        print("❌ Method must be 'ssim' or 'mse'")
        method = prompt_input(
            "Choose method (ssim/mse) [ssim]: ",
            "ssim"
        ).lower()

    # Threshold
    threshold_input = prompt_input(
        "Enter change threshold (%) [10]: ",
        "10"
    )

    while True:
        try:
            threshold = float(threshold_input)
            if threshold <= 0 or threshold > 100:
                raise ValueError
            break
        except Exception:
            print("❌ Threshold must be a number between 0 and 100")
            threshold_input = prompt_input(
                "Enter change threshold (%) [10]: ",
                "10"
            )

    print("\n🚀 Running change detection...\n")

    runner = ChangeDetectionRunner(
        input_dir=input_dir,
        output_dir=output_dir,
        method=method,
        threshold=threshold
    )

    runner.run()

    print("\n✅ Change detection complete.")
    print(f"📂 Output saved to: {output_dir}\n")


if __name__ == "__main__":
    main()
