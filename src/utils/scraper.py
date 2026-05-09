import sys
import os
import re
import requests
from bs4 import BeautifulSoup
import argparse
from pathlib import Path
import pandas as pd
from tabulate import tabulate
from src.utils.browser import fetch_html
from rapidfuzz import process, fuzz


class OurAirportsScraper:

    def __init__(self):
        self.top_airports_path = "data/raw/top_airports_2025.csv"
        self.airport_names_codes = "https://www.bts.gov/topics/airlines-and-airports/world-airport-codes"
        self.our_airports_path = "https://ourairports.com/airports/"
        self.airport_names_codes_alt = "https://www.airportcodes.us/us-airports.htm"
        self.agent = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
                      "Accept-Language": "en-US,en;q=0.9",
                     }
        self.writeout_path = "extract/"

    # helper function to pull top 50 airports into a list
    # limit is a parameter to determine limited N records
    def get_top_airports(self, n_size: int = None, limit: bool = False):

        airport_names = []

        with open(self.top_airports_path, "r") as f:
            header = next(f)  # skip header

            for line in f:
                line = line.strip()

                pattern = r"\((.*)\)"
                match = re.search(pattern, line)

                if match:
                    airport_names.append(match.group(1))

                if limit and n_size is not None and len(airport_names) >= n_size:
                    break

        print(f"number of aviation hubs: {len(airport_names)}")
        return airport_names

    # method to extract official IATA code for airports
    # note: fetches all airports not top 50
    def get_airport_codes_by_names(self, airport_names: list):

        html = fetch_html(self.airport_names_codes) # call browser automation
        soup = BeautifulSoup(html, "html.parser")

        tables = soup.find_all("table")
        target_table = None

        # search table headers contain code and city:airport
        for table in tables:

            headers = [th.get_text(strip=True) for th in table.find_all("th")]
            if headers == ["Code", "City: Airport"]:

                target_table = table
                break

        if not target_table:
            return []

        rows = target_table.find_all("tr")

        data = []
        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) < 2:
                continue

            code = cols[0].get_text(strip=True)
            name = cols[1].get_text(strip=True)

            data.append((code, name))


        # debugging
        print(f"total airports and their codes found {len(data)}")

        return data

    # get data for top 50 airports
    def get_top_airport_names_codes(self, airports: list[str], airports_codes: list[tuple[str, str]], threshold: int = 95):

        matched_airports = {}
        airport_list = airports
        airport_list_lower = [a.lower() for a in airport_list]

        for code, raw_text in airports_codes:

            pattern = r"(^.*): (.*)"
            match = re.search(pattern, raw_text)

            if not match:
                continue

            city_state = match.group(1)
            name = match.group(2).strip()

            # find one and only high matching string
            result = process.extractOne(
                name.lower(),
                airport_list_lower,
                scorer=fuzz.WRatio
            )

            if result is None:
                continue

            _, score, idx = result
            matched_name = airport_list[idx]

            if score >= threshold and matched_name not in matched_airports:

                # edge case for airports in outside regions of "mainland"
                region = "mainland US"
                
                if code == "SJU":
                    icao_code = "TJSJ"
                    region = "Contiguous US"
                elif code == "HNL":
                    icao_code = "PHNL"
                    region = "Hawaii"
                else:
                    icao_code = "K" + code

                matched_airports[matched_name] = {
                    "code": icao_code,
                    "name": matched_name,
                    "city_state": city_state,
                    "country": "USA",
                    "region": region
                }

            # stopping criterion
            if len(matched_airports) == len(airport_list):
                break

        ordered_results = []
        for i, name in enumerate(airport_list):
            if name in matched_airports:
                ordered_results.append(matched_airports[name])
            else:
                # Default ICAO if fuzzy fails
                ordered_results.append({
                    "code": "K" + name[:3].upper(),
                    "name": name,
                    "city_state": "Unknown",
                    "country": "USA",
                    "region": "mainland US"
                })

        print(f"(1): top airports retrieved, length({len(ordered_results)})")
        return ordered_results


    # method for extracting our airports detailed information about airports
    def get_our_airports_detailed(self, codes: list):

        results = []
        session = requests.Session()

        for code in codes:

            # edge case for airports with poor naming convention
            extra_codes = {
                "HNL": "NHL",
                "STL": "STL",
                "CMH": "CMH"
            }

            if code in extra_codes:
                code = extra_codes[code] # get accurate code

            url = f"{self.our_airports_path}{code}/"

            try:
                res = session.get(url, headers=self.agent, timeout=5)
            except Exception:
                continue

            if res.status_code != 200:
                continue

            soup = BeautifulSoup(res.text, "html.parser")
            table = soup.find("table", class_="small table table-striped")

            if not table:
                continue

            airport_data = {
                "iata_code": None,
                "icao_code": None,
                "facility_type": None,
                "latitude": None,
                "longitude": None,
                "elevation_ft": None,
                "elevation_m": None,
            }

            for row in table.find_all("tr"):
                th = row.find("th")
                td = row.find("td")

                if not th or not td:
                    continue

                key = th.get_text(strip=True).lower()
                value = td.get_text(" ", strip=True)

                if key == "iata code":
                    airport_data["iata_code"] = value

                elif key == "icao code":
                    airport_data["icao_code"] = value

                elif key == "facility type":
                    airport_data["facility_type"] = value

                elif key == "coordinates":
                    
                    # parse coordinate pair into separate columns
                    coord_text = value.split()[0]
                    lat, lon = coord_text.split(",")

                    airport_data["latitude"] = float(lat)
                    airport_data["longitude"] = float(lon)

                elif key == "field elevation":

                    clean = value.replace("\xa0", " ")

                    # html raw content clean up with regex
                    ft_match = re.search(r"([\d,]+)\s*ft", clean)
                    m_match = re.search(r"([\d,]+)\s*m", clean)

                    if ft_match:
                        airport_data["elevation_ft"] = int(ft_match.group(1).replace(",", ""))

                    if m_match:
                        airport_data["elevation_m"] = int(m_match.group(1).replace(",", ""))

            results.append(airport_data)

        return results

    # read all contents of airport metadata to JSON
    def read_to_csv(self, data: pd.DataFrame, output_path: str):

        # note: using Path lib instead of os
        path = Path(output_path)

        path.parent.mkdir(parents=True, exist_ok=True)

        data.to_csv(path, index=False)

    # insert hardcoded missing data at a specific rank
    def insert_missing_data(self, data: pd.DataFrame) -> pd.DataFrame:
        
        # case: missing Columbus airport at rank 49 (index 48)
        # in all fuzzy case attempts, Columbus airport is always missed
        if "John Glenn Columbus International" not in data["name"].values:

            columbus_row = pd.DataFrame([{
                "name": "John Glenn Columbus International",
                "city_state": "Columbus, OH",
                "country": "USA",
                "region": "mainland US",
                "iata_code": "CMH",
                "icao_code": "KCMH",
                "facility_type": "large_airport",
                "latitude": 39.998001,
                "longitude": -82.891899,
                "elevation_ft": 815,
                "elevation_m": 248
            }])
            
            if len(data) >= 48:
                data = pd.concat([data.iloc[:48], columbus_row, data.iloc[48:]]).reset_index(drop=True)
            else:
                data = pd.concat([data, columbus_row]).reset_index(drop=True)
                
        return data
# execution

def main():

    # create scraper instance
    scraper = OurAirportsScraper()
    parser = argparse.ArgumentParser(description="scraper cli")

    parser.add_argument("--scrape", type=int, help="Number of top airports")
    parser.add_argument("--save", type=str, help="Output file path")

    args = parser.parse_args()

    print("(1) fetching top airports")
    airports = scraper.get_top_airports(
        args.scrape,
        limit=(args.scrape is not None)
    )

    print("(2) fetching airport codes")
    airports_codes = scraper.get_airport_codes_by_names(airports)
    top_airport_names_codes = scraper.get_top_airport_names_codes(
        airports,
        airports_codes
    )

    codes_found = [d.get("code", "Unknown") for d in top_airport_names_codes]

    print("(3) fetching airport details")
    airport_detailed = scraper.get_our_airports_detailed(codes_found)

    df_l = pd.DataFrame(top_airport_names_codes)
    df_r = pd.DataFrame(airport_detailed)

    df_joined = df_l.merge(
        df_r,
        how="inner",
        left_on="code",
        right_on="icao_code"
    )

    df_joined = df_joined.drop(columns=["code"], errors="ignore")
    df_joined = scraper.insert_missing_data(df_joined)

    if args.save:
        scraper.read_to_csv(df_joined, args.save)
        print(f"Saved data to {args.save}")
    else:
        print(tabulate(df_joined, tablefmt="psql", showindex=False, headers="keys"))


if __name__ == "__main__":
    main()


