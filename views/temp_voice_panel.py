import discord
from discord.ext import commands


class RenameModal(discord.ui.Modal, title="Renommer le salon"):
    new_name = discord.ui.TextInput(
        label="Nouveau nom",
        style=discord.TextStyle.short,
        max_length=100,
        required=True,
    )

    def __init__(self, channel: discord.VoiceChannel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            await self.channel.edit(name=str(self.new_name))
            await interaction.followup.send(
                f"Salon renommé en **{self.new_name}**.", ephemeral=True
            )
        except discord.HTTPException:
            # Rate limit Discord : 2 renames / 10 min per channel
            await interaction.followup.send(
                "Impossible de renommer maintenant (limite Discord, réessaie dans quelques minutes).",
                ephemeral=True,
            )

class LimitModal(discord.ui.Modal, title="Limiter le salon"):
    new_limit = discord.ui.TextInput(
        label="Nouvelle limite (0 = illimité)",
        style=discord.TextStyle.short,
        max_length=3,
        required=True,
    )

    def __init__(self, channel: discord.VoiceChannel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)


        try:
            limit = int(self.new_limit.value)
        except ValueError:
            await interaction.followup.send(
                "Merci d'entrer un nombre valide.", ephemeral=True
            )
            return

        if not (0 <= limit <= 99):
            await interaction.followup.send(
                "La limite doit être comprise entre 0 (illimité) et 99.", ephemeral=True
            )
            return

        try:
            await self.channel.edit(user_limit=limit)
            texte_limite = "illimitée" if limit == 0 else f"{limit} personnes"
            await interaction.followup.send(
                f"Salon limité à **{texte_limite}**.", ephemeral=True
            )
        except discord.HTTPException as e:
            await interaction.followup.send(
                f"Erreur lors de la modification : {e}", ephemeral=True
            )

class ControlPanel(discord.ui.View):
    def __init__(self, channel: discord.VoiceChannel, owner_id: int):
        super().__init__(timeout=None)
        self.channel = channel
        self.owner_id = owner_id

    async def check_owner(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "Seul le propriétaire du salon peut faire ça.", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Renommer", style=discord.ButtonStyle.primary)
    async def rename_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_owner(interaction):
            return
        await interaction.response.send_modal(RenameModal(self.channel))

    @discord.ui.button(label="Limiter", style=discord.ButtonStyle.secondary)
    async def limit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_owner(interaction):
            return
        await interaction.response.send_modal(LimitModal(self.channel))
