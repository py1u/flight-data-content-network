import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tabulate import tabulate


class OurAirportsScraper:
    def __init__(self):
        pass

    def request_content(self, url):
        pass

    # get data for single airport
    def request_airport(self, url):
        pass

    # read all contents of airport metadata to csv
    def read_to_csv(self:
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

    return scraper.extract_top_airports("https://view.officeapps.live.com/op/embed.aspx?src=https://www.bts.dot.gov/sites/bts.dot.gov/files/2026-03/table_01_44_032626.xlsx&wdAllowInteractivity=False&wdDownloadButton=False&ActiveCell=A1")


