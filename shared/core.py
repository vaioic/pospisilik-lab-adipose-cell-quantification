from pathlib import Path

import numpy as np
import pandas as pd
import scipy.ndimage as ndi
import skimage
from oic_toolkit.display import merge_images
from openslide import OpenSlide
from tqdm import tqdm

from shared import core

# Generate custom color map
CUSTOM_COLORS = (np.random.default_rng(seed=42)).uniform(0.1, 1.0, size=(100, 3))


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


def process_directory(input_path, output_path, skip_done=True, **kwargs):

    input_path = Path(input_path)

    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    # Find all SVS files
    slide_file_list = list(input_path.glob("*.svs"))

    all_data = []
    for file in tqdm(slide_file_list):
        # Check if there's already an output file
        if skip_done and (output_path / f"{file.stem}.csv").exists():
            print("Output CSV exists. Skipping file.")
            continue

        try:
            df = process_slide(file, output_path, **kwargs)
            all_data.append(df)
        except Exception as e:
            print(f"An error occurred: {type(e).__name__} - {e}")

    combined_df = pd.concat(all_data)

    combined_df.to_csv(output_path / "combined_data.csv")


def process_slide(
    slide_path,
    output_path,
    save_data=True,
    min_cell_size=500,
    max_cell_size=50000,
    roi=None,
):

    slide_path = Path(slide_path)

    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    img = core.read_image_from_slide(slide_path)

    if roi is not None:
        img = img[roi[0] : roi[1], roi[2] : roi[3]]

    img_filt = ndi.median_filter(img, size=3)

    # import matplotlib.pyplot as plt

    # fig, ax = skimage.filters.try_all_threshold(img_filt)
    # plt.show()
    # exit()

    # Identify the adipose tissue
    th = skimage.filters.threshold_mean(img_filt)
    adipose_mask = img_filt > th
    # print(th)

    # import matplotlib.pyplot as plt

    # plt.imshow(adipose_mask)
    # plt.show()
    # exit()

    adipose_mask = skimage.segmentation.clear_border(adipose_mask)

    # # Try to connect the lines
    # adipose_mask_boundaries = ~adipose_mask

    # adipose_mask_boundaries_ds = skimage.transform.rescale(
    #     adipose_mask_boundaries, 0.5, anti_aliasing=None, order=0, preserve_range=True
    # )

    # adipose_mask_boundaries_closed = skimage.morphology.closing(
    #     adipose_mask_boundaries_ds, skimage.morphology.disk(15)
    # )

    # adipose_mask_boundaries_ds_merged = (
    #     adipose_mask_boundaries_ds ^ adipose_mask_boundaries_closed
    # )

    # import matplotlib.pyplot as plt

    # plt.imshow(adipose_mask_boundaries_ds_merged)
    # plt.show()
    # exit()

    adipose_mask = skimage.morphology.remove_small_holes(adipose_mask, max_size=3000)
    adipose_mask = skimage.morphology.remove_small_objects(
        adipose_mask, max_size=min_cell_size
    )

    if max_cell_size is not None:
        # Remove large objects
        adipose_mask_large = skimage.morphology.remove_small_objects(
            adipose_mask, max_size=max_cell_size
        )

        adipose_mask = adipose_mask ^ adipose_mask_large

    # Measure and export data to CSV
    labels = skimage.measure.label(adipose_mask, connectivity=1)
    data = skimage.measure.regionprops_table(labels, properties=("area",))

    df = pd.DataFrame(data)
    df["Image"] = slide_path.stem

    if save_data:
        fn = slide_path.stem
        df.to_csv(output_path / f"{fn}.csv", index=False)

        # Create output image
        try:
            ds_img = skimage.transform.rescale(img, 0.25)
            ds_labels = skimage.transform.rescale(
                labels, 0.25, order=0, anti_aliasing=False, preserve_range=True
            )

            merged = merge_images(
                ds_img,
                skimage.color.label2rgb(
                    ds_labels, bg_color="black", colors=CUSTOM_COLORS
                ),
                mode="blend",
            )

            skimage.io.imsave(output_path / f"{fn}_overlay.png", merged)
        except MemoryError as e:
            print(f"Out of memory when generating merged image: {e}")

    return df
