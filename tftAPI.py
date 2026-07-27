import requests
import os

RIOT_API_KEY = os.getenv("RIOT_API_KEY")

def get_tft_rank(puuid, cpid):
    region = cpid.lower()

    headers = {
        "X-Riot-Token": RIOT_API_KEY
    }

    url = f"https://{region}.api.riotgames.com/tft/league/v1/by-puuid/{puuid}"

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200:

        data = response.json()
        for queue in data:
            if queue.get("queueType") == "RANKED_TFT":
                return queue["tier"]

        return "UNRANKED"
    return None