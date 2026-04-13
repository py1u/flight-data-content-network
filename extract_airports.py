import requests
from bs4 import BeautifulSoup


class OurAirportsScraper:
    BASE_URL = "https://ourairports.com/airports"

    def __init__(self, timeout=10):
        self.session = requests.Session()
        self.timeout = timeout

    def fetch_airport_page(self, icao: str) -> str:
        url = f"{self.BASE_URL}/{icao}/"
        res = self.session.get(url, timeout=self.timeout)

        if res.status_code != 200:
            raise Exception(f"Failed to fetch {icao}: {res.status_code}")

        return res.text

    def parse_airport_data(self, html: str) -> dict:
        soup = BeautifulSoup(html, "html.parser")

        data = {}

        # 1. Airport name (header)
        header = soup.find("h1")
        if header:
            data["name"] = header.text.strip()

        # 2. Extract table key-value pairs
        tables = soup.find_all("table")

        for table in tables:
            rows = table.find_all("tr")

            for row in rows:
                cols = row.find_all(["th", "td"])
                if len(cols) == 2:
                    key = cols[0].text.strip().lower().replace(" ", "_")
                    value = cols[1].text.strip()
                    data[key] = value

        # 3. Extract coordinates if present
        coord_tag = soup.find("a", href=lambda x: x and "maps.google.com" in x)
        if coord_tag:
            data["map_link"] = coord_tag["href"]

        return data

    def get_airport(self, icao: str) -> dict:
        html = self.fetch_airport_page(icao)
        return self.parse_airport_data(html)


if __name__ == "__main__":
    scraper = OurAirportsScraper()

    airport = scraper.get_airport("EGLL")

    for k, v in airport.items():
        print(f"{k}: {v}")