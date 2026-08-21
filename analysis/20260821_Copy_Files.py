from shared import core

# Copy data to local drive using the information from the CSV-file

core.copy_files(
    r"..\data\dataset01\eWAT_sWAT_Images to Analyze_BG.csv",
    r"\\pn.vai.org\projects\pospisilik\primary\vari-core-generated-data\PBC-Aperio Images",
    r"..\data\dataset01",
)
