import os
import glob
import json
import pandas as pd

def process_meteo_json_files(input_dir: str, output_dir: str):

    print("starting METEO data cleaning...")
    
    os.makedirs(output_dir, exist_ok=True)
    json_files = glob.glob(os.path.join(input_dir, "*_meteo_2025.json"))
    
    processed_count = 0
    for json_file in json_files:

        filename = os.path.basename(json_file)
        
        airport_code = filename.split("_meteo_2025.json")[0]
        
        with open(json_file, 'r', encoding='utf-8') as f:
            meteo_json = json.load(f)
            
        hourly_df = pd.DataFrame(meteo_json.get("hourly", {}))
        daily_df = pd.DataFrame(meteo_json.get("daily", {}))
        
        # metadata extraction: the coordinates for each aiport
        lat = meteo_json.get("latitude")
        lon = meteo_json.get("longitude")
        
        if not hourly_df.empty and not daily_df.empty:

            hourly_df["date"] = hourly_df["time"].str.split("T").str[0]
            df = pd.merge(hourly_df, daily_df, left_on="date", right_on="time", how="left", suffixes=("", "_daily"))

            if "time_daily" in df.columns:

                df = df.drop(columns=["time_daily"])

        elif not hourly_df.empty:
            df = hourly_df

        else:
            df = daily_df
            
        if not df.empty:
            df["airport_code"] = airport_code

            if lat is not None:
                df["latitude"] = lat

            if lon is not None:
                df["longitude"] = lon
            
            # ending csv path
            csv_filename = f"{airport_code}_meteo_2025.csv"
            csv_path = os.path.join(output_dir, csv_filename)
            df.to_csv(csv_path, index=False)

            # report cleaned and saved file
            print(f"Processed and saved {csv_filename}")
            processed_count += 1

    # debugging        
    print(f"Cleaned {processed_count} files.")


    return processed_count

def main():

    # handle errors for local path imports to pull raw data
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    input_dir = os.path.join(project_root, "data", "raw", "meteo")
    output_dir = os.path.join(project_root, "data", "processed", "meteo")
    
    process_meteo_json_files(input_dir, output_dir)

if __name__ == "__main__":
    main()
