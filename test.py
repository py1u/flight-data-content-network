import requests
from bs4 import BeautifulSoup
import re
import time

# function to collect BTS airport data for all common airports
def fetch_bts_airport_directory(ss: requests.Session, url: str, agent: dict, max_tries: int = 5, backoff: int = 1.5):

    for attempt in range(max_tries):
            try:
                res = ss.get("https://www.transtats.bts.gov/", headers=agent , timeout=5)
                time.sleep(backoff)

                # successful response return data
                if res.status_code == 200:
                    return res

                print(f"Request failed with status code: {res.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt+1} error: {e}")




    soup = BeautifulSoup(res.text, "html.parser")

    airports = []

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

url = "https://www.transtats.bts.gov/NewAirportList.asp?Acntr=nv421465.n52&synt=SNPgf"

airports = fetch_airport_links(url)

for a in airports[:10]:
    print(a)