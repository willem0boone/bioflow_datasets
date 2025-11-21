import imageio
from pathlib import Path
from PIL import Image


def pngs_to_gif(input_files, output_gif, duration=0.8):
    """
    Create a GIF from a list of PNG files.

    Parameters
    ----------
    input_files : list or str or Path
        A list of PNG file paths, or a directory containing PNGs.
    output_gif : str or Path
        The output GIF filename.
    duration : float
        Time (seconds) each frame is shown.
    """
    input_files = Path(input_files)

    # If a directory is passed, get all PNGs sorted by name
    if input_files.is_dir():
        png_files = sorted(input_files.glob("*.png"))
    else:
        png_files = [Path(f) for f in input_files]

    if not png_files:
        raise ValueError("No PNG files found to create GIF.")

    # Load first image to get reference size
    first_img = Image.open(png_files[0])
    w, h = first_img.size

    frames = []
    for f in png_files:
        img = Image.open(f)

        # Resize if needed
        if img.size != (w, h):
            img = img.resize((w, h), Image.LANCZOS)

        frames.append(img)

    # Save GIF
    frames[0].save(
        output_gif,
        save_all=True,
        append_images=frames[1:],
        duration=int(duration * 1000),
        loop=0
    )

    print(f"GIF saved to {output_gif}")


# ------------------------------------------------------------
# ✅ Minimal main block (using your real directory)
# ------------------------------------------------------------
if __name__ == "__main__":

    input_dir = r"C:\Users\willem.boone\Documents\projects\dto-bioflow\datasets\pythonProject\plots\map_per_dasid"
    output_gif = r"C:\Users\willem.boone\Documents\projects\dto-bioflow\datasets\pythonProject\plots\maps.gif"

    pngs_to_gif(input_dir, output_gif, duration=0.8)
