import discord
from discord import app_commands
from utils.jsonStorage import load_data, save_data
from tftAPI import get_tft_rank, RiotAPIError
import asyncio

async def update_rank(interaction: discord.Interaction, member: discord.Member):
    data = load_data()
    member_id = str(member.id)

    if member_id not in data["riot_links"]:
        return f"<@{member.id}> n'a pas lié son compte riot."

    old_rank = data["riot_links"][member_id]["tft_rank"]
    puuid = data["riot_links"][member_id]["puuid"]
    cpid = data["riot_links"][member_id]["cpid"]

    try:
        current_rank = await asyncio.to_thread(get_tft_rank, puuid, cpid)
    except RiotAPIError as e:
        return f"<@{member.id}> : erreur API Riot ({e})"

    role_id = data.get(f"tft_rank_{current_rank}_role_id")
    role = interaction.guild.get_role(role_id)

    if current_rank != old_rank:
        data["riot_links"][member_id]["tft_rank"] = current_rank
        save_data(data)
        try:
            await member.add_roles(role)
            await member.remove_roles(interaction.guild.get_role(data.get(f"tft_rank_{old_rank}_role_id")))
        except discord.Forbidden:
            return "Le rôle est trop haut dans la hiérarchie."
        except discord.HTTPException as e:
            return f"Erreur lors de l'ajout du rôle : {e}"

        return f"<@{member.id}> a eu son rôle mis a jour !"
    else:
        if role not in member.roles: 
            try:
                await member.add_roles(role)
            except discord.Forbidden:
                return "Le rôle est trop haut dans la hiérarchie."
            except discord.HTTPException as e:
                return f"Erreur lors de l'ajout du rôle : {e}"
            return f"<@{member.id}> a eu son rôle mis a jour !"

        return f"<@{member.id}> avait déjà le bon rôle."

class UpdateRankView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔄 Update ton rank", style=discord.ButtonStyle.gray, custom_id="UpdateRankView")
    async def rename_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        message = await update_rank(interaction, interaction.user)
        
        await interaction.response.send_message(message, ephemeral=True)

def setup(bot):
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @bot.tree.command(name="update_rank", description="Met a jour le rank du membre choisi")
    @app_commands.describe(member="Le membre qui va avoir son rank mis a jour")
    async def update_rank_command(interaction: discord.Interaction, member: discord.Member):

        message = await update_rank(interaction, member)

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
        updated_count = 0
        errors = 0

        for i, member in enumerate(members):
            try:
                await update_rank(interaction, member)
                updated_count += 1
            except Exception as e:
                errors += 1
                print(f"Erreur pour {member}: {e}")

            await asyncio.sleep(0.3)

            if (i + 1) % 5 == 0 or i==0:
                try:
                    await interaction.edit_original_response(
                        content=f"Progression : {i + 1}/{len(members)} membres traités..."
                    )
                except discord.HTTPException:
                    pass

        await interaction.followup.send(
            f"Mise à jour terminée : {updated_count} succès, {errors} erreur(s) sur {len(members)} membres.",
            ephemeral=True
        )
