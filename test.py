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


# helper to parse the extracted data for single airport(table 1)
def _parse_summary_table(table):

    rows = table.find_all("tr")

    headers = []
    data = []
    current_section = None

    for i, row in enumerate(rows):

        cols = row.find_all(["td", "th"])
        values = [c.get_text(strip=True) for c in cols]

        if not values:
            continue

        if i == 0:

            headers = values
            headers[0] = "metric"
            continue

        if len(cols) == 1 or cols[0].has_attr("colspan"):

            current_section = values[0]
            continue

        row_dict = dict(zip(headers, values))
        row_dict["section"] = current_section
        data.append(row_dict)

    return data


# helper to normalize data for tabular format
def _normalize_value(val):
    if not val:
        return None

    # clean data of markings
    val = val.replace(',', '')

    if val.endswith('k'):
        return float(val[:-1]) * 1_000

    if val.endswith('m'):
        return float(val[:-1]) * 1_000_000

    if '%' in val:
        return float(val.replace('%', ''))

    try:
        return float(val)

    except:
        return val

# helper function to clean up table label and output format
def _to_tidy_format(data):
    tidy = []

    for row in data:
        base = {
            "section": row["section"],
            "metric": row["metric"],
            "pct_change": _normalize_value(row["%Chg"]),
            "rank": _normalize_value(row["Rank***"])
        }

        for year_col in ["2025**", "2026**"]:
            tidy.append({
                **base,
                "year": int(year_col[:4]),
                "value": _normalize_value(row[year_col])
            })

    return tidy

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

                # parse html data tables for US flights
                th = soup.find("th", string=lambda s: s and "Summary Data (U.S. Flights Only)" in s)

                if not th:
                    return None

                td = th.find_parent("tr").find("td")
                table = td.find("table")

                # container = th.find_parent("tr")
                #
                # tables = container.find_all("table")
                #
                # parsed_tables = []
                #
                # for table in tables:
                #     rows = table.find_all("tr")
                #
                #     parsed = []
                #
                #     for row in rows:
                #         cols = row.find_all(["td", "th"])
                #         parsed.append([c.get_text(strip=True) for c in cols])
                #
                #     parsed_tables.append(parsed)
                #
                # return parsed_tables

                # call helper functions to prepare data
                parsed = _parse_summary_table(table)
                tidy_data = _to_tidy_format(parsed)

                return tidy_data

            else:
                print(f"Attempt {attempt + 1} failed with status code: {res.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} error: {e}")

        time.sleep(backoff ** attempt)

    raise Exception(f"Failed to fetch data for airport after {max_tries} attempts")

# function to pull simple data on airport for redirect use
def fetch_single_airport_simple(data: list[dict], keyword: str, threshold: int = 70):

    airport_map = {airport["name"]: airport for airport in data}
    names = list(airport_map.keys())

    # only extract one single best match
    result = process.extractOne(
        keyword,
        names,
        scorer=fuzz.WRatio
    )

    if result is None:
        print("No matches found.")
        return None

    match, score, _ = result

    # if a search query is good enough
    if score >= threshold:
        airport = airport_map[match]

        # url is cleaned up for use before displaying
        table = [[airport["name"], "https://www.transtats.bts.gov/" + airport["url"].split(" ")[0]]]
        headers = ["Airport Name", "URL"]

        # pretty print in tabular format
        print(f"\nMatch Score: {score}\n")
        print(tbl(table, headers=headers, tablefmt="psql"))

        return table

    else:
        # user does not have a strong enough search query
        print(f"No good match found (best: {match}, score: {score})")
        print("Try using more words or letters.")
        return None

# test
bts_url = "https://www.transtats.bts.gov/NewAirportList.asp?Acntr=nv421465.n52&synt=SNPgf" # airport table of contents
session = requests.Session()
headers = { "User-Agent": "Mozilla/5.0", "Referer": "https://www.transtats.bts.gov/" }
airports = get_bts_airports(ss=session, url=bts_url, agent=headers)

# test
# data is all fetched for bts data
single_airport = fetch_single_airport_simple(data=airports, keyword="Los Angeles")

# test
single_airport_tables = get_bts_airport_details(url=single_airport[0][1], ss=session, agent=headers)

# debugging terminal output
print(tbl(single_airport_tables, tablefmt="psql", showindex=False))



# df_test = pd.read_excel("data/table_01_44_032626.xlsx", sheet_name="1-44")
# print(df_test["Table 1-44: Passengers Boarded at the Top 50 U.S. Airports"].head(10))
# print(tbl(df_test, tablefmt="psl", showindex=False))
