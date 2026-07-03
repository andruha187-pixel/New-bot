import requests
import re

def get_metar(station="UUWW"):
    url = f"https://metar.vatsim.net/metar.php?id={station}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        metar = response.text.strip()
        if not metar or "No METAR" in metar:
            return None
        return metar
    except Exception as e:
        print(f"Ошибка VATSIM API: {e}")
        return None

def extract_temp(metar: str):
    if not metar:
        return None
    match = re.search(r"\s(M?\d{1,2})/(M?\d{1,2})", metar)
    if not match:
        return None
    temp = match.group(1)
    if temp.startswith("M"):
        return -int(temp[1:])
    return int(temp)
    
