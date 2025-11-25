import imageio
from pathlib import Path
from PIL import Image

def pngs_to_gif(input_files, output_gif, duration=0.8):
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
    """
    # If input is a directory, get all PNGs
    if isinstance(input_files, (str, Path)):
        input_files = Path(input_files)
        if input_files.is_dir():
            png_files = sorted(input_files.glob("*.png"))
        else:
            png_files = [input_files]
    else:
        # Assume list of paths
        png_files = [Path(f) for f in input_files]

    if not png_files:
        raise ValueError("No PNG files found to create GIF.")

    # Load first image to get reference size
    first_img = Image.open(png_files[0])
    w, h = first_img.size

    frames = []
    for f in png_files:
        img = Image.open(f)
        if img.size != (w, h):
            img = img.resize((w, h), Image.LANCZOS)
        frames.append(img)

    frames[0].save(
        output_gif,
        save_all=True,
        append_images=frames[1:],
        duration=int(duration * 1000),
        loop=0
    )
    print(f"GIF saved to {output_gif}")


# ------------------------
# Main block
# ------------------------
if __name__ == "__main__":
    dir_call1 = Path("../plots/observation_maps")
    dir_wp3 = Path("../plots/sensor_maps")

    png_call1 = sorted(dir_call1.glob("*.png"))
    png_wp3 = sorted(dir_wp3.glob("*.png"))
    png_all = png_call1 + png_wp3

    # Use raw strings or forward slashes for Windows paths
    output_call1 = Path(r"..\plots\map_observation.gif")
    output_sensors = Path(r"..\plots\map_sensors.gif")
    output_combined = Path(r"..\plots\map_combined.gif")

    pngs_to_gif(png_call1, output_call1, duration=0.8)
    pngs_to_gif(png_wp3, output_sensors, duration=0.8)
    pngs_to_gif(png_all, output_combined, duration=0.8)
