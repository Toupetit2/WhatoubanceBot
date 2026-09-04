import requests
import asyncio
import utils
import os
from discord.ext import tasks
from datetime import time

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


async def remove_wtb_role(member, role):
    """Retire le rôle club à un membre"""
    try:
        await member.remove_roles(role)
        print(f"INFO - Rôle club retiré à {member.name} ({member.id})", flush=True)
        return True
    except Exception as e:
        print(f"Erreur retrait rôle club pour {member.name}: {e}", flush=True)
        return False


def start_daily_club_check(bot):
    """Démarre la tâche quotidienne de vérification de l'appartenance au club"""
    
    @tasks.loop(time=time(hour=2, minute=0))  # Chaque jour à 2h du matin
    async def daily_club_check():
        print("INFO - Début de la vérification quotidienne du club WTB", flush=True)
        
        try:
            data = utils.jsonStorage.load_data()
            guild_id = int(data.get("guild_id"))
            role_id = int(data.get("club_member_role_id"))
            riot_links = data.get("riot_links", {})
            
            if not guild_id or not role_id:
                print("WARN - guild_id ou club_member_role_id n'est pas configuré", flush=True)
                return
            
            guild = bot.get_guild(guild_id)
            role = guild.get_role(role_id)
            
            if not guild or not role:
                print("WARN - Guild ou rôle introuvable", flush=True)
                return
            
            # Obtenir tous les membres avec le rôle club
            members_with_role = [m for m in guild.members if role in m.roles]
            print(f"INFO - {len(members_with_role)} membres avec le rôle club", flush=True)
            
            removed_count = 0
            checked_count = 0
            
            for member in members_with_role:
                # Récupérer les infos Riot du membre
                member_id = str(member.id)
                
                if member_id not in riot_links:
                    print(f"WARN - Pas de lien Riot pour {member.name} ({member.id})", flush=True)
                    continue
                
                try:
                    puuid = riot_links[member_id].get("puuid")
                    
                    if not puuid:
                        print(f"WARN - Pas de PUUID pour {member.name}", flush=True)
                        continue
                    
                    # Récupérer le Riot ID
                    riot_id = get_riot_id_from_puuid(puuid)
                    checked_count += 1
                    
                    # Vérifier si le membre est toujours dans le club
                    if not in_wtb_club(riot_id):
                        print(f"INFO - {riot_id} n'est plus dans le club WTB, retrait du rôle", flush=True)
                        await remove_wtb_role(member, role)
                        removed_count += 1
                    else:
                        print(f"INFO - {riot_id} toujours dans le club WTB", flush=True)
                
                except Exception as e:
                    print(f"Erreur vérification pour {member.name}: {e}", flush=True)
                    continue
            
            print(f"INFO - Vérification quotidienne terminée: {checked_count} vérifiés, {removed_count} rôles retirés", flush=True)
        
        except Exception as e:
            print(f"Erreur critique pendant la vérification quotidienne: {e}", flush=True)
    
    @daily_club_check.before_loop
    async def before_daily_check():
        await bot.wait_until_ready()
    
    daily_club_check.start()
    print("INFO - Tâche quotidienne de vérification du club WTB démarrée", flush=True)