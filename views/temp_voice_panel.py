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

class LimitSelect(discord.ui.Select):
    def __init__(self, channel: discord.VoiceChannel):
        self.channel = channel
        options = [
            discord.SelectOption(label="Illimité", value="0"),
            discord.SelectOption(label="2 personnes", value="2"),
            discord.SelectOption(label="5 personnes", value="5"),
            discord.SelectOption(label="10 personnes", value="10"),
        ]
        super().__init__(placeholder="Choisis une limite", options=options)

    async def callback(self, interaction: discord.Interaction):
        limit = int(self.values[0])
        await self.channel.edit(user_limit=limit)
        await interaction.response.edit_message(
            content=f"Limite mise à jour : {'illimitée' if limit == 0 else limit}",
            view=None,
        )


class LimitView(discord.ui.View):
    def __init__(self, channel: discord.VoiceChannel):
        super().__init__(timeout=60)
        self.add_item(LimitSelect(channel))


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
        await interaction.response.send_message(
            view=LimitView(self.channel), ephemeral=True
        )
