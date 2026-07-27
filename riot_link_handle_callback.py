import os
import base64
import requests
import asyncio
import utils.jsonStorage
import tftAPI

RSO_CLIENT_ID = os.getenv("RSO_CLIENT_ID")
RSO_CLIENT_SECRET = os.getenv("RSO_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

def handle_callback(discordAPI, bot, code, state):
    basic = base64.b64encode(f"{RSO_CLIENT_ID}:{RSO_CLIENT_SECRET}".encode()).decode()
    
    headers = {
        "Authorization": f"Basic {basic}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
        }
    print(f"INFO - Riot callback received: code={code}, state={state}", flush=True)
    token_response = requests.post("https://auth.riotgames.com/token", headers=headers, data=data, timeout=10)

    token_data = token_response.json()

    if "access_token" not in token_data:
        return "Erreur lors de l'authentification Riot.", 400
    
    access_token = token_data["access_token"]

    user_info_response = requests.get(
        "https://auth.riotgames.com/userinfo",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    user_info = user_info_response.json()
    print(f"INFO - Riot user info: {user_info}", flush=True)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    print(f"DEBUG - Fetching Riot account info", flush=True)
    account_info_response = requests.get("https://europe.api.riotgames.com/riot/account/v1/accounts/me", headers=headers, timeout=10)
    account_info = account_info_response.json()
    print(f"INFO - Riot account info: {account_info}, response={account_info_response.status_code}", flush=True)
    tft_rank = tftAPI.get_tft_rank(account_info.get("puuid"), user_info.get("cpid"))

    data = utils.jsonStorage.load_data()
    data["riot_links"][str(state)] = {
        "riot_id": account_info.get("puuid"),
        "riot_name": user_info.get("name"),
        "riot_tag": user_info.get("tag_line"),
        "tft_rank": tft_rank
    }

    print(f"INFO - Riot account info saved for user {state}", flush=True)
    #give role based on rank
    if tft_rank:
        coro = discordAPI.give_role(bot, int(data["guild_id"]), int(state), int(data["tft_rank_" + tft_rank + "_role_id"]))
        future = asyncio.run_coroutine_threadsafe(coro, bot.loop)

        try:
            future.result(timeout=10)  # attend le résultat (ou lève l'exception)
        except Exception as e:
            return f"Erreur give_role: {e}"
        
        guild_id = int(data["guild_id"])
        member = bot.get_guild(guild_id).get_member(int(state))
        current_role_ids = {r.id for r in member.roles} if member else set()

        for role in ["UNRANKED", "IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "EMERALD", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]:
            if role != tft_rank:
                other_role_id = data.get(f"tft_rank_{role}_role_id")
                if other_role_id and int(other_role_id) in current_role_ids:
                    coro = discordAPI.remove_role(
                        bot, guild_id, int(state), int(other_role_id)
                    )
                    future = asyncio.run_coroutine_threadsafe(coro, bot.loop)

                    def _on_done(f, role=role):
                        if f.exception():
                            print(f"Erreur remove_role ({role}): {f.exception()}", flush=True)

                    future.add_done_callback(_on_done)

    utils.jsonStorage.save_data(data)

    return "✅ Compte Riot lié avec succès ! Tu peux fermer cette page.", 200