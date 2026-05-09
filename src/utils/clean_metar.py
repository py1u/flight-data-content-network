import os
from pathlib import Path
import pandas as pd

def clean_metar_data(filepath: Path, output_dir: Path):

    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    extracted_data = []
    in_block = False
    
    for line in lines:
        if line.startswith("#  METAR/SPECI from"):

            in_block = True
            continue
            
        # stop if we try to reach TAF reports section
        if in_block and line.startswith("# No short TAF reports"):

            in_block = False
            break
            
        if in_block and not line.startswith("#") and line.strip():

            extracted_data.append(line.strip())
            
    if extracted_data:

        df = pd.DataFrame(extracted_data, columns=["raw_metar"])

        output_dir.mkdir(parents=True, exist_ok=True)
        out_file = output_dir / f"{filepath.stem}_cleaned.csv"

        # write to csv
        df.to_csv(out_file, index=False)

        # debug
        print(f"Cleaned data saved to {out_file}")

def process_all_metar(input_dir: str = "data/raw/meteo", output_dir: str = "data/processed/metar"):

    # handle errors for local path imports to pull raw data
    project_root = Path(os.getcwd())
    
    
    in_path = project_root / input_dir
    out_path = project_root / output_dir
    
    if not in_path.exists():
        print(f"Input directory {in_path} does not exist.")
        return
    
    in_path = Path(input_dir)
    out_path = Path(output_dir)
    
    if not in_path.exists():

        print(f"Input directory {in_path} does not exist.")
        return
        
    for filepath in in_path.glob("*.txt"):

        clean_metar_data(filepath, out_path)

if __name__ == "__main__":
    process_all_metar()