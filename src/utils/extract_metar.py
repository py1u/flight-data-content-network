import time
import requests
from datetime import datetime
from calendar import monthrange
from pathlib import Path

# general root url
BASE_URL = "https://www.ogimet.com/display_metars2.php"

"""
- example full url with query params(for reference): https://www.ogimet.com/display_metars2.php?lang=en&lugar=KATL&tipo=ALL&ord=REV&nil=SI&fmt=txt&ano=2026&mes=05&day=07&hora=06&anof=2026&mesf=05&dayf=08&horaf=06&minf=59&send=send 
"""

# helper function to define all query parameters
# note airport_code is the ICAO code
def build_metar_params(airport_icao: str, year: int, month: int):

    last_day = monthrange(year, month)[1]
    # all query params share the same format and range
    return {
        "lang": "en",
        "lugar": airport_icao,
        "tipo": "ALL",
        "ord": "REV",
        "nil": "SI",
        "fmt": "txt",

        # start
        "ano": year,
        "mes": month,
        "day": 1,
        "hora": 0,

        # end
        "anof": year,
        "mesf": month,
        "dayf": last_day,
        "horaf": 23,
        "minf": 59,

        "send": "send"
    }


# note: using ICAO airport code
def extract_metar_data(airport_code: str, year: int, out_dir: str = "data/raw/metar"):

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    for month in range(1, 13):

        params = build_metar_params(airport_code, year, month)

        response = requests.get(BASE_URL, params=params, timeout=60)
        response.raise_for_status()

        # name and write file to output
        filename = f"{airport_code}_{year}_{month:02d}.txt"
        file_path = out_path / filename
        file_path.write_text(response.text, encoding="utf-8")

        # debugging
        print(f"Saved: {file_path}")
        
        # small delay to prevent rate-limiting
        time.sleep(1)

