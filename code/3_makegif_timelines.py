import imageio
from pathlib import Path
from PIL import Image


def pngs_to_gif(input_files, output_gif, duration=0.2, last_frame_hold=5):
    """
    Create a GIF from a list of PNG files.

    Parameters
    ----------
    input_files : list or Path
        A list of PNG file paths, or a directory containing PNGs.
    output_gif : str or Path
        The output GIF filename.
    duration : float
        Time (seconds) each frame is shown.
    last_frame_hold : float
        Time (seconds) to hold the last frame before looping.
    """
    from pathlib import Path
    from PIL import Image

    # Get PNG files
    if isinstance(input_files, (str, Path)):
        input_files = Path(input_files)
        if input_files.is_dir():
            png_files = sorted([f for f in input_files.glob("*.png") if f.is_file()])
        else:
            if input_files.suffix.lower() == ".png" and input_files.is_file():
                png_files = [input_files]
            else:
                png_files = []
    else:
        png_files = [Path(f) for f in input_files if Path(f).is_file() and Path(f).suffix.lower() == ".png"]

    if not png_files:
        raise ValueError(f"No PNG files found in {input_files} to create GIF.")

    # Load first image to get reference size
    first_img = Image.open(png_files[0])
    w, h = first_img.size

    frames = []
    for f in png_files:
        img = Image.open(f)
        if img.size != (w, h):
            img = img.resize((w, h), Image.LANCZOS)
        frames.append(img)

    # Add extra frames to hold the last image
    extra_frames = int(last_frame_hold / duration)
    frames.extend([frames[-1]] * extra_frames)

    frames[0].save(
        output_gif,
        save_all=True,
        append_images=frames[1:],
        duration=int(duration * 1000),
        loop=0
    )
    print(f"GIF saved to {output_gif}")


if __name__ == "__main__":
    timeline_dir = Path("../plots/timeline")

    outdir = timeline_dir

    # List all timeline subdirectories
    subdirs = [d for d in timeline_dir.iterdir() if d.is_dir()]
    print(subdirs)

    for sub in subdirs:
        gif_path = outdir / f"{sub.name}.gif"
        print(f"[START] Creating GIF for {sub.name} ...")
        pngs_to_gif(sub, gif_path, duration=0.2)
        print(f"[DONE] {gif_path}")
