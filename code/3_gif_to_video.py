from moviepy import VideoFileClip
from pathlib import Path


def gif_to_mp4(gif_path: Path, output_path: Path = None, fps: int = 24):
    """
    Converts a GIF to MP4.

    Parameters:
    - gif_path: Path to the input GIF file.
    - output_path: Optional path for the output MP4. If None, it will create one next to the GIF.
    - fps: Frames per second for the output MP4.
    """
    if output_path is None:
        output_path = gif_path.with_suffix(".mp4")

    # Load the GIF
    clip = VideoFileClip(str(gif_path))

    # Write to MP4
    clip.write_videofile(str(output_path), codec="libx264", fps=fps)
    clip.close()  # Close the clip to free resources
    print(f"Converted {gif_path} -> {output_path}")


if __name__ == "__main__":
    gif1 = Path("../plots/map_combined.gif")
    gif2 = Path("../plots/timeline/source_all_combined_log.gif")

    gif_to_mp4(gif1)
    gif_to_mp4(gif2)
