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

class TwitchLinkViewManager: 
    
    def __init__(self, bot, twitch_linker, discordAPI): 
        self.bot = bot 
        self.twitch_linker = twitch_linker 
        self.discordAPI = discordAPI 
    
    async def init(self): 
        with open("data.json", "r") as f: 
            data = json.load(f) 
        
        if "twitch_link_panel" in data: 
            message_id = data["twitch_link_panel"]["message_id"] 
            channel_id = data["twitch_link_panel"]["channel_id"] 
            channel = self.bot.get_channel(channel_id) 
            
            if channel: 
                if channel.fetch_message(message_id): 
                    self.bot.add_view(TwitchLinkView(self.twitch_linker, self.discordAPI))