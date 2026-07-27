import discord
import json
from discordAPI import DiscordAPI
import requests
import dotenv
from utils.jsonStorage import load_data, save_data

RSO_CLIENT_ID = dotenv.get_key('.env', 'RSO_CLIENT_ID')
RSO_CLIENT_SECRET = dotenv.get_key('.env', 'RSO_CLIENT_SECRET')

class LinkView(discord.ui.View): 
    
    def __init__(self, discordAPI, twitch_linker):
        super().__init__(timeout=None)
        self.discordAPI = discordAPI
        self.twitch_linker = twitch_linker
    
    @discord.ui.button(label="⬜ Lier mon Riot", style=discord.ButtonStyle.red, custom_id="riot_link_button") 
    async def riot_link_button(self, interaction: discord.Interaction, button: discord.ui.Button): 
        discord_id = str(interaction.user.id) 

        redirect_uri = 'https://bot.whatoubance.fr/oauth/callback'
        auth_url = f"https://auth.riotgames.com/authorize?client_id={RSO_CLIENT_ID}&redirect_uri={redirect_uri}&response_type=code&scope=openid+cpid&state={discord_id}&ui_locales=fr-FR"
        await interaction.response.send_message( f"👉 [Clique ici pour lier ton Riot]({auth_url})", ephemeral=True ) 

    @discord.ui.button(label="🟪 Lier mon Twitch", style=discord.ButtonStyle.blurple, custom_id="twitch_link_button") 
    async def twitch_link_button(self, interaction: discord.Interaction, button: discord.ui.Button): 
        discord_id = str(interaction.user.id) 
        auth_url = self.twitch_linker.get_auth_url(discord_id) 
        await interaction.response.send_message( f"👉 [Clique ici pour lier ton Twitch]({auth_url})", ephemeral=True, suppress_embeds=True) 

    @discord.ui.button(label="🔔 Notifs Twitch", style=discord.ButtonStyle.gray, custom_id="twitch_notification_button") 
    async def twitch_notification_button(self, interaction: discord.Interaction, button: discord.ui.Button): 
        data = load_data()
        role = interaction.guild.get_role(data["twitch_notification_role"])
        
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"Rôle **{role.name}** retiré.", ephemeral=True)
        else:
            try:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"Rôle **{role.name}** ajouté !", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message(
                    "Je n'ai pas la permission d'attribuer ce rôle.",
                    ephemeral=True,
                )
    
        