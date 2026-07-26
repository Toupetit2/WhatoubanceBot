import discord
from discord import app_commands
from views.twitch_link_views import TwitchLinkView
from utils.jsonStorage import load_data, save_data


def setup(bot, twitch_linker, discord_api):
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @bot.tree.command(name="link_twitch", description="Envoyer le panneau de liaison Twitch")
    async def link_twitch_command(interaction: discord.Interaction, role: discord.Role):
        view = TwitchLinkView(twitch_linker, discord_api)

        msg = await interaction.channel.send(
            "Clique sur le bouton pour connecter ton compte Twitch et obtenir le rôle WTB_Twitch !",
            view=view
        )

        data = load_data()
        data["guild_id"] = interaction.guild.id
        data["wtb_twitch_role_id"] = role.id
        data["twitch_link_panel"] = {
            "message_id": msg.id,
            "channel_id": msg.channel.id
        }
        save_data(data)

        await interaction.response.send_message(
            "✅ Panneau de liaison Twitch envoyé !",
            ephemeral=True
        )