import discord
import json

class TwitchLinkView(discord.ui.View): 
    
    def __init__(self, twitch_linker, discordAPI):
        super().__init__(timeout=None)
        self.twitch_linker = twitch_linker 
        self.discordAPI = discordAPI 
    
    @discord.ui.button(label="🔗 Lier mon Twitch", style=discord.ButtonStyle.blurple, custom_id="twitch_link_button") 
    async def link_button(self, interaction: discord.Interaction, button: discord.ui.Button): 
        discord_id = str(interaction.user.id) 
        auth_url = self.twitch_linker.get_auth_url(discord_id) 
        await interaction.response.send_message( f"👉 Clique ici pour lier ton Twitch :\n{auth_url}", ephemeral=True ) 
