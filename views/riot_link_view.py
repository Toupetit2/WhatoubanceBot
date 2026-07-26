import discord
import json
from discordAPI import DiscordAPI
import requests
import dotenv
from utils.jsonStorage import load_data, save_data

RSO_CLIENT_ID = dotenv.get_key('.env', 'RSO_CLIENT_ID')
RSO_CLIENT_SECRET = dotenv.get_key('.env', 'RSO_CLIENT_SECRET')

class VerifyRiotView(discord.ui.View):
    
    def __init__(self, discordAPI):
        super().__init__(timeout=None)
        self.discordAPI = discordAPI 
    
    @discord.ui.button( label="✅ J'ai vérifié mon compte Riot", style=discord.ButtonStyle.green, custom_id="riot_verify_button" ) 
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button): 
        data = load_data()
        if data["riot_links"][str(interaction.user.id)]:
            await self.discordAPI.give_role( interaction.client, data["guild_id"], interaction.user.id, data[f"tft_rank_{data['riot_links'][str(interaction.user.id)]['tft_rank']}_role_id"] )
            await interaction.response.send_message( "✅ Compte Riot vérifié !", ephemeral=True )
        else:
            await interaction.response.send_message( "❌ Compte Riot non lié !", ephemeral=True )

class RiotLinkView(discord.ui.View): 
    
    def __init__(self, discordAPI):
        super().__init__(timeout=None)
        self.discordAPI = discordAPI 
    
    @discord.ui.button(label="🔗 Lier mon Riot", style=discord.ButtonStyle.blurple, custom_id="riot_link_button") 
    async def link_button(self, interaction: discord.Interaction, button: discord.ui.Button): 
        discord_id = str(interaction.user.id) 

        redirect_uri = 'https://bot.whatoubance.fr/oauth/callback'
        auth_url = f"https://auth.riotgames.com/authorize?client_id={RSO_CLIENT_ID}&redirect_uri={redirect_uri}&response_type=code&scope=openid+cpid&state={discord_id}&ui_locales=fr-FR"
        await interaction.response.send_message( f"👉 [Clique ici pour lier ton Riot]({auth_url})",view=VerifyRiotView(self.discordAPI), ephemeral=True ) 

