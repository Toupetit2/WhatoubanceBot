"""
Script à lancer UNE FOIS pour nettoyer les membres qui ont plusieurs rôles
de rang TFT en même temps (garde uniquement le plus haut).

Utilisation :
    python clean_rank_roles.py

Nécessite les mêmes variables d'env que ton bot (au minimum DISCORD_TOKEN
et GUILD_ID), et le fichier utils/jsonStorage.py + data.json accessibles
dans le même dossier / PYTHONPATH que ton projet.
"""

import asyncio
import os
import discord
from utils.jsonStorage import load_data

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

RANK_TIERS = [
    "IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM",
    "EMERALD", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"
]

def rank_value(rank: str) -> int:
    if not rank:
        return -1
    tier = rank.upper()
    if tier not in RANK_TIERS:
        return -1
    return RANK_TIERS.index(tier)

intents = discord.Intents.default()
intents.members = True  # nécessaire pour lister guild.members

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Connecté en tant que {client.user}")

    data = load_data()
    guild = client.get_guild(GUILD_ID)

    if guild is None:
        print("Guild introuvable, vérifie GUILD_ID.")
        await client.close()
        return

    # role_id -> rang
    rank_role_ids = {}
    for rank in RANK_TIERS:
        role_id = data.get(f"tft_rank_{rank}_role_id")
        if role_id:
            rank_role_ids[int(role_id)] = rank

    if not rank_role_ids:
        print("Aucun rôle de rang configuré dans data.json.")
        await client.close()
        return

    members = guild.members
    total = len(members)
    cleaned_count = 0
    errors = 0

    print(f"{total} membres à vérifier...")

    for i, member in enumerate(members, start=1):
        member_rank_roles = [
            (role, rank_role_ids[role.id])
            for role in member.roles
            if role.id in rank_role_ids
        ]

        if len(member_rank_roles) > 1:
            best_role, best_rank = max(
                member_rank_roles, key=lambda rr: rank_value(rr[1])
            )
            roles_to_remove = [r for r, _ in member_rank_roles if r != best_role]

            try:
                await member.remove_roles(*roles_to_remove, reason="Nettoyage doublons de rangs")
                cleaned_count += 1
                names = ", ".join(r.name for r in roles_to_remove)
                print(f"[{i}/{total}] {member} : gardé {best_role.name}, retiré {names}")
            except discord.Forbidden:
                errors += 1
                print(f"[{i}/{total}] {member} : rôle trop haut dans la hiérarchie, impossible de retirer.")
            except discord.HTTPException as e:
                errors += 1
                print(f"[{i}/{total}] {member} : erreur HTTP ({e})")

            await asyncio.sleep(0.3)  # évite le rate limit Discord

    print(f"\nTerminé : {cleaned_count} membre(s) nettoyé(s), {errors} erreur(s) sur {total} membres.")
    await client.close()


client.run(DISCORD_TOKEN)