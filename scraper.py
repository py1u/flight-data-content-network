import sys
import os
import re
import requests
from bs4 import BeautifulSoup
import argparse
import pandas as pd
from tabulate import tabulate
from browser import fetch_html
from rapidfuzz import process, fuzz

"""
TODO: refactor airports to "aviation hubs" to follow FAA and BTS designations
"""

class OurAirportsScraper:

    def __init__(self):
        self.top_airports_path = "data/top_airports_2025.csv" # given
        self.airport_names_codes = "https://www.bts.gov/topics/airlines-and-airports/world-airport-codes"
        self.our_airports_path = "https://ourairports.com/airports/"
        self.airport_names_codes_alt = "https://www.airportcodes.us/us-airports.htm"
        self.agent = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
                      "Accept-Language": "en-US,en;q=0.9",
                     }

    # helper function to pull top 50 airports into a list
    # limit is a parameter to determine limited N records
    def get_top_airports(self, n_size: int, limit=False):

        airport_names = []

        with open(self.top_airports_path, "r") as f:

            count = 0
            header = next(f) # first line is a header -> skip
            for line in f:

                # early stopping condition
                if count >= n_size:
                    break

                line = line.strip()
                pattern = r"\((.*)\)"
                match = re.search(pattern,line)

                if match:
                    airport_names.append(match.group(1))

                count += 1

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

        return data

    # get data for top 50 airports
    # threshold is pre-determined and not configurable by the user
    def get_top_airport_names_codes(self, airports: list[str], airports_codes: list[tuple[str, str]], threshold: int = 93):

        matched_airports = {}
        airport_list = airports
        airport_list_lower = [a.lower() for a in airport_list]

        for code, raw_text in airports_codes:

            pattern = r"(^.*): (.*)"
            match = re.search(pattern, raw_text)

            if not match:
                # print(f"failed to find match for {(code, raw_text)}")
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
                icao_code = code

                if code == "SJU":
                    icao_code = "TJSJ"
                    region = "Contiguous US"

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
            if len(matched_airports) == 50:
                break


        ordered_results = [
            matched_airports[name]
            for name in airport_list
            if name in matched_airports
        ]

        # print(f"(1): top airports retrieved, length({len(ordered_results)})")
        return ordered_results


    # method for extracting our airports detailed information about airports
    def get_our_airports_detailed(self, codes: list):

        # store resulting records
        results = []

        session = requests.Session()

        for code in codes[:5]:

            # url path
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
                "code": code
            }

            rows = table.find_all("tr")

            for row in rows:
                th = row.find("th")
                td = row.find("td")

                if not th or not td:
                    continue

                key = th.get_text(strip=True).lower()

                if key == "tags":
                    tags = [a.get_text(strip=True) for a in td.find_all("a") if a.get("href", "").startswith("/tags")]
                    airport_data["tags"] = tags

                elif key == "location":

                    parts = [x.strip() for x in td.stripped_strings]
                    parts = [p.replace(",", "") for p in parts]

                    airport_data["city"] = parts[0] if len(parts) > 0 else None
                    airport_data["region"] = parts[1] if len(parts) > 1 else None
                    airport_data["country"] = parts[2] if len(parts) > 2 else None

                elif key == "coordinates":

                    # parse split strings
                    coord_text = list(td.stripped_strings)[0]
                    lat, lon = coord_text.split(",")

                    airport_data["latitude"] = float(lat)
                    airport_data["longitude"] = float(lon)

                elif key == "field elevation":
                    elevation = td.get_text(" ", strip=True)
                    airport_data["elevation"] = elevation

                else:
                    value = td.get_text(" ", strip=True)

                    key = key.replace(" ", "_").replace("?", "").replace("/", "").lower()

                    airport_data[key] = value

            results.append(airport_data)

        return results

    # read all contents of airport metadata to JSON
    def read_to_csv(self):
        pass

# execution
def main():
    scraper = OurAirportsScraper()

    parser = argparse.ArgumentParser(description="scraper cli")
    parser.add_argument(
        "--scrape",
        type=int,
        help="Number of top airports to scrape"
    )

    args = parser.parse_args()
    scrape_n = args.scrape

    if scrape_n is not None:
        airports = scraper.get_top_airports(scrape_n, limit=True)
    else:
        airports = scraper.get_top_airports(None, limit=False)


    airports_codes = scraper.get_airport_codes_by_names(airports) # all airports(US)
    top_airport_names_codes = scraper.get_top_airport_names_codes(airports, airports_codes)

    # get top airports and codes
    names_found = [ d.get("names", "Unknown") for d in top_airport_names_codes]
    codes_found = [ d.get("code", "Unknown") for d in top_airport_names_codes]
    # print(codes_found)

    print(tabulate(top_airport_names_codes, tablefmt="psql", headers="keys"))

    airport_detailed = scraper.get_our_airports_detailed(codes_found[:5])
    print(airport_detailed[0])

if __name__ == "__main__":
    main()


