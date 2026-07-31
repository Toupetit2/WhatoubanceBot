import discord
from discord import app_commands
from discord.ext import commands
import utils.jsonStorage as utils
import views.temp_voice_panel
import whitelist

class TempVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.panels: dict[int, views.temp_voice_panel.ControlPanel] = {} #channel_id, ControlPanel
        self.data = utils.load_data()

        raw = self.data.get("temp_channels", [])
        self.temp_channels = set(raw)

        self.bot.temp_voice_channel_id = self.data.get("temp_voice_channel_id")

        self.join_order: dict[int, list[int]] = {}

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
        if before.channel == after.channel:
            return
        # Create
        if after.channel and self.bot.temp_voice_channel_id and after.channel.id == self.bot.temp_voice_channel_id:
            new_channel_name = f"Salon de {member.display_name}"
            new_channel = await after.channel.category.create_voice_channel(new_channel_name)
            await member.move_to(new_channel)

            self.temp_channels.add(new_channel.id)
            self.persist()

            view = views.temp_voice_panel.ControlPanel(new_channel, member.id)
            await new_channel.send(f"<@{member.id}> - Commandes pour gérer le salon : ", view=view)

            self.panels[new_channel.id] = view

            self.join_order[new_channel.id] = [member.id]


        elif after.channel and after.channel.id in self.temp_channels:
            order = self.join_order.setdefault(after.channel.id, [])
            if member.id not in order:
                order.append(member.id)

        if not before.channel or before.channel.id not in self.temp_channels:
            return

        channel = before.channel

        order = self.join_order.get(channel.id, [])
        if member.id in order:
            order.remove(member.id)
        #delete
        if len(channel.members) == 0:
            await channel.delete()
            self.temp_channels.discard(channel.id)
            self.panels.pop(channel.id, None)
            self.join_order.pop(channel.id, None)
            self.persist()
            return
        #change owner
        panel = self.panels.get(channel.id)
        if panel is None:
            print(f"Error: ControlPanel introuvable pour le salon temporaire {channel.id}")
            return

        if member.id == panel.owner_id:
            new_owner = None

            for uid in order:
                m = channel.guild.get_member(uid)
                if m and m in channel.members:
                    new_owner = m
                    break

            if new_owner is None and channel.members:
                new_owner = channel.members[0]

            if new_owner:
                old_owner_id = panel.owner_id

                try:
                    await channel.set_permissions(member, overwrite=None)

                    old_whitelist = whitelist.get_whitelist(old_owner_id)
                    for uid in old_whitelist:
                        m = channel.guild.get_member(uid)
                        if m is not None and m.id != new_owner.id:
                            await channel.set_permissions(m, overwrite=None)

                    await channel.set_permissions(new_owner, connect=True)

                    new_whitelist = whitelist.get_whitelist(new_owner.id)
                    for uid in new_whitelist:
                        m = channel.guild.get_member(uid)
                        if m is not None:
                            await channel.set_permissions(m, connect=True)

                except discord.HTTPException as e:
                    print(f"Erreur lors du transfert de permissions : {e}")

                panel.owner_id = new_owner.id
                print(self.join_order)
                await channel.send(
                    f"👑 {member.display_name} a quitté le salon. "
                    f"{new_owner.mention} est le nouveau propriétaire (présent depuis le plus longtemps).",
                )

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