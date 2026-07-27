import discord
from discord import app_commands
from utils.jsonStorage import load_data, save_data
from views.link_view import LinkView


def setup(bot, discord_api, twitch_linker):
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @bot.tree.command(name="link_riot", description="Envoyer le panneau de liaison Riot")
    async def link_riot_command(interaction: discord.Interaction, role: discord.Role):
        view = LinkView(discord_api, twitch_linker)

        msg = await interaction.channel.send(
            "Clique sur le bouton pour connecter ton compte Riot et obtenir le rôle lié a ton rang !",
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
            "✅ Panneau de liaison Riot envoyé !",
            ephemeral=True
        )

    
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @bot.tree.command(name="setup_rank_roles", description="Configurer les rôles de rang TFT")
    async def setup_rank_roles_command(interaction: discord.Interaction, iron_role: discord.Role, bronze_role: discord.Role, silver_role: discord.Role, gold_role: discord.Role, platinum_role: discord.Role, emerald_role: discord.Role, diamond_role: discord.Role, master_role: discord.Role, grandmaster_role: discord.Role, challenger_role: discord.Role):
        data = load_data()
        data["guild_id"] = interaction.guild.id
        data["tft_rank_IRON_role_id"] = iron_role.id
        data["tft_rank_BRONZE_role_id"] = bronze_role.id
        data["tft_rank_SILVER_role_id"] = silver_role.id
        data["tft_rank_GOLD_role_id"] = gold_role.id
        data["tft_rank_PLATINUM_role_id"] = platinum_role.id
        data["tft_rank_EMERALD_role_id"] = emerald_role.id
        data["tft_rank_DIAMOND_role_id"] = diamond_role.id
        data["tft_rank_MASTER_role_id"] = master_role.id
        data["tft_rank_GRANDMASTER_role_id"] = grandmaster_role.id
        data["tft_rank_CHALLENGER_role_id"] = challenger_role.id
        save_data(data)

        await interaction.response.send_message(
            "✅ Rôles de rang TFT configurés avec succès !",
            ephemeral=True
        )
