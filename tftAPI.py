import requests
import os

RIOT_API_KEY = os.getenv("RIOT_API_KEY")

def get_tft_rank(puuid, cpid):
    region = cpid.lower()

    headers = {
        "X-Riot-Token": RIOT_API_KEY
    }

    url = f"https://{region}.api.riotgames.com/tft/league/v1/by-puuid/{puuid}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data:
            if data[0]['tier'] != 'UNRANKED':
                return data[0]['tier']  # Assuming the first entry is the relevant one
            return None
