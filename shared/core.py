from pathlib import Path

import numpy as np
import pandas as pd
import scipy.ndimage as ndi
import skimage
from oic_toolkit.display import merge_images
from openslide import OpenSlide
from tqdm import tqdm

from shared import core


def read_image_from_slide(slide_path):

    slide = OpenSlide(slide_path)

    img = slide.read_region(location=(0, 0), level=0, size=(slide.dimensions))
    img = np.array(img.convert("L"))

    return img


def copy_files(csv_path, source_dir, destination_dir):

    import csv
    import shutil

    source_dir = Path(source_dir)

    # Validate the source directory
    if not source_dir.exists():
        raise FileNotFoundError(f"Could not find source directory {source_dir}")

    destination_dir = Path(destination_dir)
    destination_dir.mkdir(exist_ok=True, parents=True)

    # Read in filenames from the CSV-file
    files_to_copy = []
    with open(csv_path, mode="r") as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip header

        for row in reader:
            if row and len(row) >= 2:
                files_to_copy.append(row[1] + ".svs")

    with tqdm(files_to_copy, unit="file") as pbar:
        for filename in pbar:
            # Aperio Image ID = Col 2
            source_path = source_dir / filename

            pbar.set_description(f"Copying {filename}")

            if filename == ".svs":
                tqdm.write("Empty row.")
                continue

            if not source_path.exists():
                raise FileNotFoundError(f"Could not find source file {source_path}.")

            if (destination_dir / filename).exists():
                tqdm.write(f"{filename} already exists at the destination. Skipping.")
                continue

            try:
                new_path = shutil.copy2(source_path, destination_dir)
            except FileNotFoundError:
                print(
                    "Error: The source file or destination directory could not be found."
                )
            else:
                print("Skipping file.")


def process_directory(input_path, output_path):

    input_path = Path(input_path)

    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    # Find all SVS files
    slide_file_list = list(input_path.glob("*.svs"))

    all_data = []
    for file in tqdm(slide_file_list):
        df = process_slide(file, output_path)

        all_data.append(df)

    combined_df = pd.merge(all_data)

    combined_df.to_csv(output_path / "combined_data.csv")


def process_slide(slide_path, output_path, save_data=True):

    slide_path = Path(slide_path)

    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    img = core.read_image_from_slide(slide_path)

    img_filt = ndi.median_filter(img, size=3)

    # Identify the adipose tissue
    adipose_mask = img_filt > 240

    adipose_mask = skimage.segmentation.clear_border(adipose_mask)

    adipose_mask = skimage.morphology.remove_small_holes(adipose_mask, max_size=150)
    adipose_mask = skimage.morphology.remove_small_objects(adipose_mask, max_size=500)

    # Measure and export data to CSV
    labels = skimage.measure.label(adipose_mask)
    data = skimage.measure.regionprops_table(labels, properties=("area",))

    df = pd.DataFrame(data)
    df["Image"] = slide_path.stem

    if save_data:
        fn = slide_path.stem
        df.to_csv(output_path / f"{fn}.csv", index=False)

        # Create output image
        merged = merge_images(
            img, skimage.color.label2rgb(labels, bg_color="black"), mode="blend"
        )

        skimage.io.imsave(output_path / f"{fn}_overlay.png", merged)

    return df
