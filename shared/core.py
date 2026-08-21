from pathlib import Path

from tqdm import tqdm


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


def main():
    print("Hello from template-analysis-uv!")


if __name__ == "__main__":
    main()
