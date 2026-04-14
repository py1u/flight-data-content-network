import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
from tabulate import tabulate as tbl

# function to collect BTS airport data for all common US airports
# note: part of web scraping for data ingestion
def get_bts_airports(ss: requests.Session, url: str, agent: dict, max_tries: int = 5, backoff: int = 1.5):

    for attempt in range(max_tries):
        try:
            res = ss.get(url, headers=agent, timeout=5)

            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                airports = []

                # look for all links towards page links(anchor tags)
                for a in soup.find_all("a", href=True):
                    href = a["href"]

                    match = re.search(r"window_Close\('(.+?)'\)", href)

                    if match:
                        extracted_url = match.group(1)
                        airport_name = a.text.strip()

                        airports.append({
                            "name": airport_name,
                            "url": extracted_url
                        })

                return airports

            else:
                print(f"Attempt {attempt+1} failed with status code: {res.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt+1} error: {e}")

        time.sleep(backoff ** attempt)

    raise Exception(f"Failed to fetch BTS airports after {max_tries} attempts")

# same input data except for the url which must be a single airport
def get_bts_airport_details(ss: requests.Session, url: str, agent: dict, max_tries: int = 5, backoff: int = 1.5):
    pass


# test
bts_url = "https://www.transtats.bts.gov/NewAirportList.asp?Acntr=nv421465.n52&synt=SNPgf"
session = requests.Session()
headers = { "User-Agent": "Mozilla/5.0", "Referer": "https://www.transtats.bts.gov/" }

airports = get_bts_airports(ss=session, url=bts_url, agent=headers)

for airport in airports[:10]:
    print(airport)

# df_test = pd.read_excel("data/table_01_44_032626.xlsx", sheet_name="1-44")
# print(df_test["Table 1-44: Passengers Boarded at the Top 50 U.S. Airports"].head(10))
# print(tbl(df_test, tablefmt="psl", showindex=False))
