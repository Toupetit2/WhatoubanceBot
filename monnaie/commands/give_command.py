import discord
from discord import app_commands
import monnaie.give as give

def setup(bot):
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @bot.tree.command(name="give_coins", description="Donne X coins au membre")
    async def give_coins_command(interaction: discord.Interaction, member: discord.Member):
        give(10, member)

        await interaction.response.send_message("a", ephemeral=True)