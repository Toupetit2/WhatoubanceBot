import requests
import os

RIOT_API_KEY = os.getenv("RIOT_API_KEY")

def get_tft_rank(puuid, cpid):
    region = cpid.lower()

    headers = {
        "X-Riot-Token": RIOT_API_KEY
    }

    url = f"https://{region}.api.riotgames.com/tft/league/v1/by-puuid/{puuid}"
    print(f"DEBUG - request riot api", flush=True)
    response = requests.get(url, headers=headers, timeout=10)
    print(f"DEBUG - Riot response code: {response.status_code}", flush=True)
    if response.status_code == 200:
        print(f"DEBUG - 200 code", flush=True)
        data = response.json()
        if data:
            if data[0]['tier'] != 'UNRANKED':
                return data[0]['tier']  # Assuming the first entry is the relevant one
            return 'UNRANKED'
