import discord
from discord import app_commands
from utils.jsonStorage import load_data, save_data
import tftAPI
import discordAPI

def setup(bot):
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @bot.tree.command(name="update_rank", description="Met a jour le rank du membre choisi")
    @app_commands.describe(member="Le membre qui va avoir son rank mis a jour")
    async def link_command(interaction: discord.Interaction, member: discord.Member):
        
        data = load_data()

        old_rank = data["riot_links"][member.id]["tft_rank"]

        puuid = data["riot_links"][member.id]["puuid"]
        cpid = data["riot_links"][member.id]["cpid"]

        current_rank = tftAPI.get_tft_rank(puuid, cpid)

        if current_rank != old_rank:

            role = interaction.guild.get_role(data.get(f"tft_rank_{old_rank}_role_id"))
            try:
                await member.add_roles(role)
            except discord.Forbidden:
                await interaction.response.send_message("Le rôle est trop haut dans la hiérarchie.")
            except discord.HTTPException as e:
                await interaction.response.send_message(f"Erreur lors de l'ajout du rôle : {e}")

            await interaction.response.send_message(
                f"<@{member.id}> a eu son rôle mis a jour !",
                ephemeral=True
            )
        await interaction.response.send_message(
                    f"<@{member.id}> avait déjà le bon role. ",
                    ephemeral=True
                )