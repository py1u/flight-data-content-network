from pathlib import Path
import pandas as pd
import os

# config fixed columns list
COLUMNS_TO_KEEP = [
    "FL_DATE",
    "CRS_DEP_TIME",
    "DEP_TIME",
    "CRS_ARR_TIME",
    "ARR_TIME",
    "ORIGIN_AIRPORT_ID",
    "ORIGIN",
    "DEST_AIRPORT_ID",
    "DEST",
    "DEP_DELAY",
    "ARR_DELAY",
    "DEP_DEL15",
    "ARR_DEL15",
    "DEP_DELAY_GROUP",
    "ARR_DELAY_GROUP",
    "TAXI_OUT",
    "TAXI_IN",
    "CANCELLED",
    "CANCELLATION_CODE",
    "DIVERTED",
]

MONTH_MAP = {
    "JANUARY": "01",
    "FEBURARY": "02",
    "MARCH": "03",
    "APRIL": "04",
    "MAY": "05",
    "JUNE": "06",
    "JULY": "07",
    "AUGUST": "08",
    "SEPTEMBER": "09",
    "OCTOBER": "10",
    "NOVEMBER": "11",
    "DECEMBER": "12"
}

# must be all files in data/raw/bts to be processed
# note: the data is already bulk uploaded and clean_bts.py will perform data transformation]

def extract_bts_data(raw_dir: str = "../../data/raw/bts", processed_dir: str = "../../data/processed/bts"):

    # get current paths
    project_root = Path(os.getcwd())
    raw_path = project_root / raw_dir
    out_path = project_root / processed_dir
    out_path.mkdir(parents=True, exist_ok=True)

    csv_files = list(raw_path.glob("T_ONTIME_REPORTING_*.csv"))

    if not csv_files:

        print(f"No CSV files found in {raw_path}")
        return

    def get_month_num(filepath):
        
        # rename and clean up file naming
        month_str = filepath.stem.replace("T_ONTIME_REPORTING_", "").upper()
        return MONTH_MAP.get(month_str, "99")

    # sort files by month order
    csv_files.sort(key=get_month_num)

    for file in csv_files:

        month_str = file.stem.replace("T_ONTIME_REPORTING_", "").upper()
        month_num = MONTH_MAP.get(month_str)
        
        if not month_num:

            # debugging
            print(f"Skipping {file.name}, could not parse month.")
            continue

        df = pd.read_csv(file, low_memory=False)
        cols = [c for c in COLUMNS_TO_KEEP if c in df.columns]

        # curr column reduced dataframe
        df = df[cols]

        output_file_name = f"bts_{month_num}_2025.csv"
        output_file = out_path / output_file_name

        # write to csv format
        df.to_csv(output_file, index=False)

        # debugging
        print(f"Processed: {file.name} -> {output_file.name}")

    # debugging
    print(f"Processed {len(csv_files)} BTS files.")


if __name__ == "__main__":
    extract_bts_data()