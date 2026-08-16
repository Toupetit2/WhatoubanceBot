import requests
import os
from rate_limiter import RateLimiter
import time

RIOT_API_KEY = os.getenv("RIOT_API_KEY")
riot_limiter_short = RateLimiter(max_calls=500, period=10)
riot_limiter_long = RateLimiter(max_calls=30000, period=600)


class RiotAPIError(Exception):
    """Erreur inattendue lors de l'appel à l'API Riot."""
    pass


def get_tft_rank(puuid, cpid, max_retries=3):
    region = cpid.lower()
    headers = {"X-Riot-Token": RIOT_API_KEY}
    url = f"https://{region}.api.riotgames.com/tft/league/v1/by-puuid/{puuid}"

    for attempt in range(max_retries):
        riot_limiter_short.acquire()
        riot_limiter_long.acquire()

        try:
            response = requests.get(url, headers=headers, timeout=10)
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise RiotAPIError(f"Erreur réseau vers l'API Riot : {e}")
            time.sleep(1)
            continue

        if response.status_code == 200:
            data = response.json()
            for queue in data:
                if queue.get("queueType") == "RANKED_TFT":
                    return queue["tier"]
            return "UNRANKED"

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 1))
            time.sleep(retry_after)
            continue

        if response.status_code == 404:
            return None

        # 401/403 = clé invalide/expirée, 5xx = souci côté Riot
        raise RiotAPIError(
            f"Riot API a répondu {response.status_code} pour {puuid} ({region})"
        )

    raise RiotAPIError(f"Échec après {max_retries} tentatives (429 répétés) pour {puuid}")