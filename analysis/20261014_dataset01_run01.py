from pathlib import Path

import pandas as pd

# from shared import core

# # core.process_directory(
# #     "../data/dataset01",
# #     "../processed/2026-10-15",
# #     min_cell_size=500,
# #     max_cell_size=None,
# #     skip_done=False,
# # )

# Do the CSV-merging since I made a mistake in the processing code (fixed for later
# versions)
MICRONSPPSQ = 0.5031**2

output = Path("../processed/2026-10-15")
csv_list = list(output.glob("*.csv"))

all_data = []

summary_stats = []

for f in csv_list:
    df = pd.read_csv(f)
    print("Exact columns found:", df.columns.tolist())

    all_data.append(df)

    # Calculate summary stats
    stats = {
        "Image": df["Image"].iloc[0],
        "Number of cells": df["area"].count(),
        "Average area (microns^2)": df["area"].mean() * MICRONSPPSQ,
        "Min area (microns^2)": df["area"].min() * MICRONSPPSQ,
        "Max area (microns^2)": df["area"].max() * MICRONSPPSQ,
        "Standard deviation area (microns^2)": df["area"].std() * MICRONSPPSQ,
    }

    df_stats = pd.DataFrame(stats, index=[0])
    summary_stats.append(df_stats)

combined_df = pd.concat(all_data)
combined_df.to_csv(output / "combined_data.csv", index=False)

combined_stats = pd.concat(summary_stats)
combined_stats.to_csv(output / "summary.csv", index=False)
