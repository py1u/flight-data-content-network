import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
from rapidfuzz import process, fuzz

from tabulate import tabulate as tbl


# function to collect BTS airport data for all common US airports
# note: part of web scraping for data ingestion
def get_bts_airports(ss: requests.Session, url: str, agent: dict, max_tries: int = 5, backoff: int = 1.5):

    for attempt in range(max_tries):
        try:
            print("fetching all airports in United States..")
            res = ss.get(url, headers=agent, timeout=5)

            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                airports = []
                count = 1

                # look for all links towards page links(anchor tags)
                for a in soup.find_all("a", href=True):
                    href = a["href"]

                    match = re.search(r"window_Close\('(.+?)'\)", href)

                    if match:
                        extracted_url = match.group(1)
                        airport_name = a.text.strip()

                        airports.append({
                            "index": count,
                            "name": airport_name,
                            "url": extracted_url
                        })

                    count += 1

                print("Successfully fetched!")
                return airports

            else:
                print(f"Attempt {attempt+1} failed with status code: {res.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt+1} error: {e}")

        time.sleep(backoff ** attempt)

    raise Exception(f"Failed to fetch BTS airports after {max_tries} attempts")

# same input data except for the url which must be a single airport
def get_bts_airport_details(ss: requests.Session, url: str, agent: dict, max_tries: int = 5, backoff: int = 1.5):
    for attempt in range(max_tries):
        try:
            res = ss.get(url, headers=agent, timeout=5)

            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                airport_data = {}

                # extract all relevant airport metadata
                scripts = soup.find_all("script")

                tbl_names =  ("Summary Data (U.S. Flights Only)", # keyword
                              "Top 10 Destination Airports (U.S. Only, Passengers (000))", # found in third div but for now do not use
                              "{airport_code_here} On-Time Performance Summary (Major U.S. Carriers Only)", # for now do not use
                              )

                # parse html data tables
                th = soup.find("th", string=lambda s: s and tbl_names[0] in s)

                if not th:
                    return None

                container = th.find_parent("tr")

                tables = container.find_all("table")

                parsed_tables = []

                for table in tables:
                    rows = table.find_all("tr")

                    parsed = []

                    for row in rows:
                        cols = row.find_all(["td", "th"])
                        parsed.append([c.get_text(strip=True) for c in cols])

                    parsed_tables.append(parsed)

                return parsed_tables

            else:
                print(f"Attempt {attempt + 1} failed with status code: {res.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} error: {e}")

        time.sleep(backoff ** attempt)

    raise Exception(f"Failed to fetch data for airport after {max_tries} attempts")


# test
bts_url = "https://www.transtats.bts.gov/NewAirportList.asp?Acntr=nv421465.n52&synt=SNPgf"
session = requests.Session()
headers = { "User-Agent": "Mozilla/5.0", "Referer": "https://www.transtats.bts.gov/" }

airports = get_bts_airports(ss=session, url=bts_url, agent=headers)

# function to pull simple data on airport for redirect use
def fetch_single_airport_simple(data: list[dict], keyword: str, threshold: int = 70):

    airport_map = {airport["name"]: airport for airport in data}
    names = list(airport_map.keys())

    # only extract single best match
    match, score, _ = process.extractOne(
        keyword,
        names,
        scorer=fuzz.WRatio
    )

    # if a search query is too small
    if score >= threshold:
        result = airport_map[match]
        print(f"Match: {match} (score: {score})")
        return result

    else:
        print(f"No good match found (best: {match}, score: {score})")
        print("try to use more words or letters.")
        return None

# test
fetch_single_airport_simple(data=airports, keyword="Los Angeles")

# df_test = pd.read_excel("data/table_01_44_032626.xlsx", sheet_name="1-44")
# print(df_test["Table 1-44: Passengers Boarded at the Top 50 U.S. Airports"].head(10))
# print(tbl(df_test, tablefmt="psl", showindex=False))
