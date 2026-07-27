import discord
from discord import app_commands
from discord.ext import commands
import utils.jsonStorage as utils

class TempVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.data = utils.load_data()
        self.temp_channels = self.data["temp_channels"] if "temp_channels" in self.data else {}


    @commands.Cog.listener()
    async def on_ready(self):
        to_remove = []
        for channel_id in self.temp_channels:
            channel = self.bot.get_channel(channel_id)

            if channel is None:
                to_remove.append(channel_id)

            elif len(channel.members) == 0:
                await channel.delete()
                to_remove.append(channel_id)

        for channel_id in to_remove:
            self.temp_channels.discard(channel_id)

        self.data["temp_channels"] = self.temp_channels
        utils.save_data(self.data)


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel and after.channel.id == self.bot.temp_voice_channel_id:
           
            new_channel_name = f"{member.display_name}'s Salon"
            new_channel = await after.channel.category.create_voice_channel(new_channel_name)
    
            await member.move_to(new_channel)            

            self.temp_channels.add(new_channel.id)

            if len(new_channel.members) == 0: 
                await new_channel.delete()
                self.temp_channels.discard(before.channel.id)

            self.data["temp_channels"] = self.temp_channels
            utils.save_data(self.data)
    

async def setup(bot):
    await bot.add_cog(TempVoice(bot))

    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @bot.tree.command(name="setup_temp_voice", description="Créer un salon vocal 'créer un salon'")
    async def setup_temp_voice_command(interaction: discord.Interaction, category: discord.CategoryChannel):
        channel_name = "➕ Créer un salon"

        # Vérifier si le salon vocal existe déjà
        existing_channel = discord.utils.get(category.voice_channels, name=channel_name)
        if existing_channel:
            await interaction.response.send_message(
                f"❌ Le salon vocal '{channel_name}' existe déjà dans cette catégorie.",
                ephemeral=True
            )
            return

        # Créer le salon vocal
        new_channel = await category.create_voice_channel(channel_name)
        bot.temp_voice_channel_id = new_channel.id  # Stocker l'ID du salon vocal dans le bot

        await interaction.response.send_message(
            f"✅ Salon vocal '{channel_name}' créé avec succès dans la catégorie '{category.name}' !",
            ephemeral=True
        )

    