import discord
from discord import app_commands
from utils.jsonStorage import load_data, save_data
from tftAPI import get_tft_rank, RiotAPIError
import asyncio
from in_club import get_riot_id_from_puuid, in_wtb_club
import requests
from discord.ext import tasks
import os

GUILD_ID = int(os.getenv("GUILD_ID"))

RANK_TIERS = [
    "IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM",
    "EMERALD", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"
]

def rank_value(rank: str) -> int:
    """
    Convertit un tier TFT (ex: 'GOLD') en valeur numérique comparable.
    Retourne -1 si le rang est inconnu/non parsable (considéré comme le plus bas).
    """
    if not rank:
        return -1

    tier = rank.upper()

    if tier not in RANK_TIERS:
        return -1

    return RANK_TIERS.index(tier)

async def update_rank(interaction: discord.Interaction, member: discord.Member, allow_downgrade: bool = True):
    data = load_data()
    member_id = str(member.id)

    if member_id not in data["riot_links"]:
        return f"<@{member.id}> n'a pas lié son compte riot.", False

    old_rank = data["riot_links"][member_id]["tft_rank"]
    puuid = data["riot_links"][member_id]["puuid"]
    cpid = data["riot_links"][member_id]["cpid"]

    try:
        current_rank = await asyncio.to_thread(get_tft_rank, puuid, cpid)
    except RiotAPIError as e:
        return f"<@{member.id}> : erreur API Riot ({e})", False

    # Vérification du club WTB
    try:
        riot_id = await asyncio.to_thread(get_riot_id_from_puuid, puuid)

        if await asyncio.to_thread(in_wtb_club, riot_id):
            club_role_id = data.get("club_member_role_id")
            club_role = interaction.guild.get_role(int(club_role_id)) if club_role_id else None

            if club_role and club_role not in member.roles:
                await member.add_roles(club_role)

    except requests.RequestException as e:
        print(f"Erreur récupération Riot ID pour {member}: {e}", flush=True)

    except discord.Forbidden:
        return "Le rôle club est trop haut dans la hiérarchie.", False

    except discord.HTTPException as e:
        return f"Erreur lors de l'ajout du rôle club : {e}", False

    role_id = data.get(f"tft_rank_{current_rank}_role_id")
    role = interaction.guild.get_role(role_id)

    if not allow_downgrade and rank_value(current_rank) < rank_value(old_rank):
        if role not in member.roles:
            try:
                await member.add_roles(role)
            except discord.Forbidden:
                return "Le rôle est trop haut dans la hiérarchie.", False
            except discord.HTTPException as e:
                return f"Erreur lors de l'ajout du rôle : {e}", False
        return f"<@{member.id}> : rang en baisse ignoré (conservé : {old_rank}).", False

    if current_rank != old_rank:
        data["riot_links"][member_id]["tft_rank"] = current_rank
        save_data(data)

        old_role = interaction.guild.get_role(data.get(f"tft_rank_{old_rank}_role_id"))
        new_roles = [r for r in member.roles if r != old_role]
        if role not in new_roles:
            new_roles.append(role)

        try:
            await member.edit(roles=new_roles)
        except discord.Forbidden:
            return "Le rôle est trop haut dans la hiérarchie.", False
        except discord.HTTPException as e:
            return f"Erreur lors de la mise à jour du rôle : {e}", False

        return f"<@{member.id}> a eu son rôle mis a jour !", True
    else:
        if role not in member.roles:
            try:
                await member.add_roles(role)
            except discord.Forbidden:
                return "Le rôle est trop haut dans la hiérarchie.", False
            except discord.HTTPException as e:
                return f"Erreur lors de l'ajout du rôle : {e}", False
            return f"<@{member.id}> a eu son rôle mis a jour !", True

        return f"<@{member.id}> avait déjà le bon rôle.", False

class UpdateRankView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔄 Update ton rank", style=discord.ButtonStyle.gray, custom_id="UpdateRankView")
    async def rename_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        message, _ = await update_rank(interaction, interaction.user)
        await interaction.response.send_message(message, ephemeral=True)

def setup(bot):
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @bot.tree.command(name="update_rank", description="Met a jour le rank du membre choisi")
    @app_commands.describe(member="Le membre qui va avoir son rank mis a jour")
    async def update_rank_command(interaction: discord.Interaction, member: discord.Member):
        message, _ = await update_rank(interaction, member)
        await interaction.response.send_message(message, ephemeral=True)


    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @bot.tree.command(name="setup_update_rank_button", description="Envoie un bouton pour pouvoir mettre a jour son rank")
    async def setup_update_rank_command(interaction: discord.Interaction):

        view = UpdateRankView()

        await interaction.channel.send(view=view)
        await interaction.response.send_message("Bouton envoyé !", ephemeral=True)

    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @bot.tree.command(name="update_rank_everyone", description="Met a jour le rank de tout le serveur")
    async def update_rank_everyone_command(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        members = interaction.guild.members
        total = len(members)

        updated_count = 0 
        changed_count = 0      
        errors = 0
        done = 0

        lock = asyncio.Lock()

        semaphore = asyncio.Semaphore(20)

        async def process(member):
            nonlocal updated_count, changed_count, errors, done
            async with semaphore:
                try:
                    _, changed = await update_rank(interaction, member)
                    updated_count += 1
                    if changed:
                        changed_count += 1
                except Exception as e:
                    errors += 1
                    print(f"Erreur pour {member}: {e}")
                finally:
                    async with lock:
                        done += 1
                        if done % 5 == 0 or done == total:
                            try:
                                await interaction.edit_original_response(
                                    content=f"Progression : {done}/{total} membres traités..."
                                )
                            except discord.HTTPException:
                                pass

                    await asyncio.sleep(0.05)

        await asyncio.gather(*(process(m) for m in members))

        await interaction.followup.send(
            f"Mise à jour terminée : {updated_count} succès ({changed_count} rôle(s) changé(s)), "
            f"{errors} erreur(s) sur {total} membres.",
            ephemeral=True
        )


    @tasks.loop(hours=1)
    async def auto_update_rank_everyone():
        guild = bot.get_guild(int(os.getenv("GUILD_ID")))
        members = guild.members
        total = len(members)
        updated_count = 0
        changed_count = 0
        errors = 0

        semaphore = asyncio.Semaphore(20)

        class _FakeInteraction:
            def __init__(self, guild):
                self.guild = guild

        fake_interaction = _FakeInteraction(guild)

        async def process(member):
            nonlocal updated_count, changed_count, errors
            async with semaphore:
                try:
                    _, changed = await update_rank(fake_interaction, member, allow_downgrade=False)
                    updated_count += 1
                    if changed:
                        changed_count += 1
                except Exception as e:
                    errors += 1
                    print(f"Erreur pour {member}: {e}")
                finally:
                    await asyncio.sleep(0.05)

        await asyncio.gather(*(process(m) for m in members))

        print(
            f"[auto_update_rank] {guild.name} : {updated_count} succès "
            f"({changed_count} changé(s)), {errors} erreur(s) sur {total} membres.",
            flush=True
        )

    @auto_update_rank_everyone.before_loop
    async def before_auto_update_rank_everyone():
        await bot.wait_until_ready()

    auto_update_rank_everyone.start()

    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @bot.tree.command(name="toggle_auto_update_rank", description="Active ou désactive la mise à jour automatique horaire des ranks")
    async def toggle_auto_update_rank_command(interaction: discord.Interaction):
        if auto_update_rank_everyone.is_running():
            auto_update_rank_everyone.cancel()
            await interaction.response.send_message("🔴 Mise à jour automatique désactivée.", ephemeral=True)
        else:
            auto_update_rank_everyone.start()
            await interaction.response.send_message("🟢 Mise à jour automatique activée (toutes les heures).", ephemeral=True)