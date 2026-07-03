# metar.py
import requests
import gzip
import io
import re

URL = "https://aviationweather.gov/data/cache/metars.cache.csv.gz"

def fetch_cache():
    try:
        r = requests.get(URL, timeout=10)
        r.raise_for_status()
        gz = gzip.GzipFile(fileobj=io.BytesIO(r.content))
        return gz.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Ошибка при скачивании кэша: {e}")
        return ""

get_metar(station="UUWW"):
    data = fetch_cache()
    for line in data.splitlines():
        if station in line:
            parts = line.split(",")
            if len(parts) > 0:
                # ИСПРАВЛЕНО: берем parts[0], где лежит сам текст METAR, 
                # и очищаем его от лишних кавычек
                return parts[0].replace('"', '').strip()
    return None

def extract_temp(metar: str):
    """
    Вытаскивает температуру из METAR (например, 23/12 или M02/05)
    """
    if not metar:
        return None
        
    match = re.search(r"\s(M?\d{1,2})/(M?\d{1,2})", metar)
    if not match:
        return None

    temp = match.group(1)
    if temp.startswith("M"):
        return -int(temp[1:])
    return int(temp)
    
