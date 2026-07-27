import discord
from discord import app_commands
from discord.ext import commands
import utils.jsonStorage as utils
import views.temp_voice_panel


class TempVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = utils.load_data()

        # On force toujours un set, peu importe ce qu'il y a dans le JSON
        raw = self.data.get("temp_channels", [])
        self.temp_channels = set(raw)

        # ID du salon "➕ Créer un salon" persisté aussi
        self.bot.temp_voice_channel_id = self.data.get("temp_voice_channel_id")

    def persist(self):
        self.data = utils.load_data()
        self.data["temp_channels"] = list(self.temp_channels)
        self.data["temp_voice_channel_id"] = self.bot.temp_voice_channel_id
        utils.save_data(self.data)

    @commands.Cog.listener()
    async def on_ready(self):
        to_remove = []
        for channel_id in list(self.temp_channels):
            channel = self.bot.get_channel(channel_id)
            if channel is None:
                to_remove.append(channel_id)
            elif len(channel.members) == 0:
                await channel.delete()
                to_remove.append(channel_id)

        for channel_id in to_remove:
            self.temp_channels.discard(channel_id)

        self.persist()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Création d'un salon temporaire
        if after.channel and self.bot.temp_voice_channel_id and after.channel.id == self.bot.temp_voice_channel_id:
            new_channel_name = f"Salon de {member.display_name}"
            new_channel = await after.channel.category.create_voice_channel(new_channel_name)
            await member.move_to(new_channel)

            self.temp_channels.add(new_channel.id)
            self.persist()

            # Control Panel
            view = views.temp_voice_panel.ControlPanel(new_channel, member.id)
            await new_channel.send("Commandes pour gérer le salon : ", view=view)

        # Suppression si un salon temporaire devient vide
        if before.channel and before.channel.id in self.temp_channels:
            if len(before.channel.members) == 0:
                await before.channel.delete()
                self.temp_channels.discard(before.channel.id)
                self.persist()


async def setup(bot):
    await bot.add_cog(TempVoice(bot))

    @bot.tree.command(name="setup_temp_voice", description="Créer un salon vocal 'créer un salon'")
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    async def setup_temp_voice_command(interaction: discord.Interaction, category: discord.CategoryChannel):
        channel_name = "➕ Créer un salon"

        existing_channel = discord.utils.get(category.voice_channels, name=channel_name)
        if existing_channel:
            await interaction.response.send_message(
                f"❌ Le salon vocal '{channel_name}' existe déjà dans cette catégorie.",
                ephemeral=True
            )
            return

        new_channel = await category.create_voice_channel(channel_name)
        bot.temp_voice_channel_id = new_channel.id

        # ⚠️ Persister l'ID pour qu'il survive à un redémarrage
        cog = bot.get_cog("TempVoice")
        cog.data["temp_voice_channel_id"] = new_channel.id
        utils.save_data(cog.data)

        await interaction.response.send_message(
            f"✅ Salon vocal '{channel_name}' créé avec succès dans la catégorie '{category.name}' !",
            ephemeral=True
        )