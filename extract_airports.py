import os
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tabulate import tabulate


class OurAirportsScraper:

    def __init__(self):
        self.top_airports_path = "data/top_airports_2025.csv" # given

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


    # get data for single airport
    def request_airport(self, url):
        pass

    # read all contents of airport metadata to csv
    def read_to_csv(self):
        pass

    # executes all pipeline
    def run_pipeline(self):
        pass

    # pass in the value of the url
    # note: "1-44" is default among government public agg spreadsheets
    def extract_top_airports(self, url, name="1-44"):

        print(f"request extraction from {url}")
        df_top_airports = pd.read_excel(url, sheet_name=name, engine="openpyxl")

        print("extraction result:")

        tblt = tabulate(df_top_airports, tablefmt="psql", showindex=False)

        return tblt


def main():

    scraper = OurAirportsScraper()

    print(scraper.get_airport_names())


if __name__ == "__main__":
    main()


