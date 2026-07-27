import discord
from discord import app_commands
from discord.ext import commands

def setup(bot):
    @app_commands.guild_only()
    @bot.tree.command(name="clear", description="Supprime les X derniers messages")
    @app_commands.describe(message_nb="Nombre de messages a supprimer")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear_command(interaction: discord.Interaction, message_nb: int):
        if message_nb < 1 or message_nb > 100:
            await interaction.response.send_message(
            "❌ Le nombre doit être entre 1 et 100.",
            ephemeral=True
        )
            return

        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=message_nb)

        await interaction.response.send_message(
            f"✅ {deleted} messages supprimés !", delete_after=10
        )