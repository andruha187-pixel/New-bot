import requests
import gzip
import io
import re

URL = "https://aviationweather.gov/data/cache/metars.cache.csv.gz"


def fetch_cache():
    r = requests.get(URL, timeout=10)
    gz = gzip.GzipFile(fileobj=io.BytesIO(r.content))
    return gz.read().decode("utf-8", errors="ignore")


def get_metar(station="UUWW"):
    data = fetch_cache()

    for line in data.splitlines():
        if station in line:
            parts = line.split(",")
            if len(parts) > 1:
                return parts[1].strip()

    return None


def extract_temp(metar: str):
    """
    Extract temperature from METAR:
    e.g. 18/12 or M02/05
    """
    match = re.search(r"\s(M?\d{1,2})/(M?\d{1,2})", metar)

    if not match:
        return None

    temp = match.group(1)

    if temp.startswith("M"):
        return -int(temp[1:])

    return int(temp)