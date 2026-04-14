import sys
import os
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tabulate import tabulate
from browser import fetch_html


class OurAirportsScraper:

    def __init__(self):
        self.top_airports_path = "data/top_airports_2025.csv" # given
        self.airport_names_codes = "https://www.bts.gov/topics/airlines-and-airports/world-airport-codes"
        self.airport_names_codes_alt = "https://www.airportcodes.us/us-airports.htm"
        self.agent = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
                      "Accept-Language": "en-US,en;q=0.9",
                     }

    # helper function to pull top 50 airports into a list
    def get_airport_names(self):

        airport_names = []

        with open(self.top_airports_path, "r") as f:

            header = next(f) # first line is a header -> skip
            for line in f:

                line = line.strip()
                pattern = r"\((.*)\)"
                match = re.search(pattern,line)

                if match:
                    airport_names.append(match.group(1))

            return airport_names

    # method to extract official IATA code for airports
    def get_airport_codes_by_names(self, airport_names: list):

        html = fetch_html(self.airport_names_codes)
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

    # get data for single airport from ourAirports
    def request_airport(self, url):
        pass

    # read all contents of airport metadata to JSON
    def read_to_csv(self):
        pass

    # executes all pipeline functions
    def run_pipeline(self):
        pass


def main():

    scraper = OurAirportsScraper()
    airports = scraper.get_airport_names()

    print(scraper.get_airport_codes_by_names(airports)[:10])

if __name__ == "__main__":
    main()


