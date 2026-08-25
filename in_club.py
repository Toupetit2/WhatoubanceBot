import requests
import asyncio
import utils
import os

RIOT_API_KEY = os.getenv("RIOT_API_KEY")

def get_riot_id_from_puuid(puuid):
    response = requests.get(
        f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}",
        headers={
            "X-Riot-Token": RIOT_API_KEY
        },
        timeout=10
    )

    response.raise_for_status()

    account = response.json()

    return f"{account['gameName']}#{account['tagLine']}"

def in_wtb_club(riotID):
    url = "https://api-ggtech.leagueoflegends.com/api/v2/public/showcase/tft-clubs-fr/teamMembers?visible=true&perPage=-1&teamSlug=whatoubance"

    response = requests.get(url)

    if response.status_code != 200:
        print("Error GGtech API:", response.text, flush=True)
        return False

    data = response.json()["returnData"]["data"]

    target = riotID.strip().casefold()

    for player in data:
        display_name = player.get("displayName", "").strip().casefold()

        if display_name == target:
            return True

        for account in player.get("gameNicks", []):
            nick = account.get("nick", "").strip().casefold()

            if nick == target:
                return True

    return False


def give_wtb_role(bot, state, account_info):
    game_name = account_info.get("gameName")
    tag_line = account_info.get("tagLine")

    if not game_name or not tag_line:
        print("WARN - Impossible de récupérer le Riot ID pour le rôle WTB", flush=True)
        return False

    riot_id = f"{game_name}#{tag_line}"

    if not in_wtb_club(riot_id):
        print(f"INFO - {riot_id} n'est pas dans le club WTB", flush=True)
        return False

    data = utils.jsonStorage.load_data()
    role_id = data.get("club_member_role_id")

    if not role_id:
        print("WARN - club_member_role_id n'est pas configuré", flush=True)
        return False

    guild = bot.get_guild(int(data["guild_id"]))
    member = guild.get_member(int(state))
    role = guild.get_role(int(role_id))

    if not member:
        print(f"WARN - Membre Discord {state} introuvable", flush=True)
        return False

    if not role:
        print(f"WARN - Rôle {role_id} introuvable", flush=True)
        return False

    coro = member.add_roles(role)

    future = asyncio.run_coroutine_threadsafe(coro, bot.loop)

    try:
        future.result(timeout=10)
        print(f"INFO - Rôle club donné à {riot_id}", flush=True)
        return True
    except Exception as e:
        print(f"Erreur ajout rôle club pour {riot_id}: {e}", flush=True)
        return False