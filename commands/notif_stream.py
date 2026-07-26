import discord
from discord import app_commands
from utils.jsonStorage import load_data, save_data


def setup(bot, twitch_bot):
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @bot.tree.command(name="add_stream", description="Ajouter un streamer à surveiller")
    async def add_stream_command(
        interaction: discord.Interaction,
        username: str,
        channel: discord.TextChannel,
        message: str = ""
    ):
        if twitch_bot.add_stream(username, channel.id, message):
            await interaction.response.send_message(
                f"✅ Streamer **{username}** ajouté avec succès !",
                ephemeral=True
            )
        else:
            channel_id = twitch_bot.get_stream_announce_channel(username)
            await interaction.response.send_message(
                f"❌ Le streamer **{username}** est déjà surveillé dans <#{channel_id}>.",
                ephemeral=True
            )

    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @bot.tree.command(name="remove_stream", description="Supprimer un streamer de la surveillance")
    async def remove_stream_command(
        interaction: discord.Interaction,
        username: str
    ):
        if twitch_bot.remove_stream(username):
            await interaction.response.send_message(
                f"✅ Streamer **{username}** supprimé avec succès !",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"❌ Impossible de supprimer **{username}** : il n'est pas surveillé.",
                ephemeral=True
            )

    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @bot.tree.command(name="list_streams", description="Afficher la liste des streamers surveillés")
    async def list_streams_command(interaction: discord.Interaction):
        streamers = twitch_bot.data["streamers"]
        if not streamers:
            await interaction.response.send_message(
                "Aucun streamer n'est actuellement surveillé.",
                ephemeral=True
            )
            return

        embed = discord.Embed(title="Streamers surveillés", color=0x9146FF)
        for username, is_live in streamers.items():
            channel = twitch_bot.get_stream_announce_channel(username)
            message = twitch_bot.get_stream_embed_message(username)
            embed.add_field(name=username, value=f"<#{channel}> {message}", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @bot.tree.command(name="modify_stream_message", description="Modifier le message d'annonce pour un streamer")
    async def modify_stream_message_command(interaction: discord.Interaction, username: str, message: str):
        if username in twitch_bot.data["streamers"]:
            twitch_bot.data["streamers_embed_message"][username] = message
            save_data(twitch_bot.data)
            await interaction.response.send_message(
                f"✅ Message d'annonce pour **{username}** mis à jour !",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"❌ Impossible de modifier le message : **{username}** n'est pas surveillé.",
                ephemeral=True
            )