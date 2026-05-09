import os
import sys
import time
import requests
import pandas as pd

# Add the project root to sys.path so we can import from util
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# define all util modules
from src.utils.scraper import OurAirportsScraper
from src.utils.extract_meteo import extract_meteo_data
from src.utils.extract_metar import extract_metar_data
from src.utils.extract_bts import extract_bts_data


def main():

    # already have airport_details so for now comment out
    # # get top 50 airports in US
    # print("Fetching top 50 airports in US...")
    # scraper = OurAirportsScraper()

    # # get top 50 airports from top_airports.csv
    # airports = scraper.get_top_airports(n_size=50)

    # # get airport names and codes
    # airports_codes = scraper.get_airport_codes_by_names(airports)

    # # get data for top 50 airports
    # top_airport_names_codes = scraper.get_top_airport_names_codes(airports, airports_codes)
    # codes_found = [d.get("code", "Unknown") for d in top_airport_names_codes]

    # # fetching airport details
    # print("Fetching airport details (this will take a moment)...")
    # airport_detailed = scraper.get_our_airports_detailed(codes_found)

    # df_l = pd.DataFrame(top_airport_names_codes)
    # df_r = pd.DataFrame(airport_detailed)

    # df_joined = df_l.merge(
    #     df_r,
    #     how="inner",
    #     left_on="code",
    #     right_on="icao_code"
    # )
    # df_joined = df_joined.drop(columns=["code"], errors="ignore")
    # df_joined = scraper.insert_missing_data(df_joined)

    # # save data to csv
    # out_path = os.path.join(project_root, "data", "raw", "airport_details.csv")
    # scraper.read_to_csv(df_joined, out_path)

    # # check result saved 
    # print(f"Saved {len(df_joined)} airport records to {out_path}")

    # load data for top airports
    csv_path = os.path.join(project_root, "data", "raw", "airport_details.csv")
    df_top_airports = pd.read_csv(csv_path)

    # get icao codes used by multiple data collection methods below
    # case: if there are NaN in the column we can drop them
    icao_codes_dropna = df_top_airports["icao_code"].dropna().tolist()

    # all data extraction method begin here:

    print("Extracting METEO data...")

    # get coordinates and codes for meteo extraction
    coords = list(df_top_airports[["latitude", "longitude"]].itertuples(index=False, name=None))
    icao_codes = df_top_airports["icao_code"].tolist()

    # debugging
    # show only top 10 coordinates
    print(coords[:10])

    # extracting meteo data
    # meteo_output_dir = os.path.join(project_root, "data", "raw", "meteo")
    # meteo_res = extract_meteo_data(coords, icao_codes, meteo_output_dir)
    # print(f"Meteo extraction completed for {len(meteo_res)} airports.")


    print("Extracting METAR historical data...")

    metar_output_dir = os.path.join(project_root, "data", "raw", "metar")
    
    for icao in icao_codes_dropna:
        extract_metar_data(icao, 2025, metar_output_dir)

    # print("Extracting BTS data...")
    # extract_bts_data()

if __name__ == "__main__":
    main()