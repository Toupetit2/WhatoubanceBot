import discord
from discord import app_commands
import Monnaie.give as give

def setup(bot):
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @bot.tree.command(name="give_coins", description="Donne X coins au membre")
    async def give_coins_command(interaction: discord.Interaction):
        give(10, interaction.user)

        await interaction.response.send_message("", ephemeral=True)