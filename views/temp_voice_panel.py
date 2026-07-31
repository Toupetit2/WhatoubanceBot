import discord
from discord.ext import commands
import whitelist

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


class ChangeOwnerView(discord.ui.View):
    def __init__(self, channel: discord.VoiceChannel, control_panel: "ControlPanel"):
        super().__init__(timeout=60)
        self.channel = channel
        self.control_panel = control_panel

        options = [
            discord.SelectOption(label=member.display_name, value=str(member.id))
            for member in channel.members
            if not member.bot and member.id != control_panel.owner_id
        ]

        if not options:
            # Personne d'éligible dans le salon
            self.select_owner.disabled = True
            options = [discord.SelectOption(label="Aucun membre disponible", value="none")]

        self.select_owner.options = options

    @discord.ui.select(placeholder="Choisis le nouveau chef du salon", min_values=1, max_values=1)
    async def select_owner(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values[0] == "none":
            return

        new_owner_id = int(select.values[0])
        new_owner = self.channel.guild.get_member(new_owner_id)

        if new_owner is None or new_owner not in self.channel.members:
            await interaction.response.send_message(
                "Ce membre n'est plus dans le salon.", ephemeral=True
            )
            return

        old_owner_id = self.control_panel.owner_id
        old_owner = self.channel.guild.get_member(self.control_panel.owner_id)

        try:
            if old_owner is not None:
                await self.channel.set_permissions(old_owner, overwrite=None)

            old_whitelist = whitelist.get_whitelist(old_owner_id)
            for member_id in old_whitelist:
                member = self.channel.guild.get_member(member_id)
                if member is not None and member.id != new_owner.id:
                    await self.channel.set_permissions(member, overwrite=None)
            
            await self.channel.set_permissions(
                new_owner, connect=True
            )
        except discord.HTTPException as e:
            await interaction.response.send_message(
                f"Erreur lors du changement de chef : {e}", ephemeral=True
            )
            return

        self.control_panel.owner_id = new_owner.id

        await interaction.response.defer()
        await interaction.delete_original_response()
        
        try:
            await self.channel.send(
                f"👑 {new_owner.mention} est désormais le chef du salon."
            )
        except discord.HTTPException:
            pass
        
class WhitelistModal(discord.ui.Modal, title="Whitelist"):
    def __init__(self, channel: discord.VoiceChannel, owner_id: int,  guild: discord.Guild):
        super().__init__()
        self.channel = channel
        self.owner_id = owner_id

        current_ids = whitelist.get_whitelist(owner_id)
        default_members = [
            discord.Object(id=uid) for uid in current_ids
            if guild.get_member(uid) is not None
        ]

        self.user_select = discord.ui.UserSelect(
            placeholder="Ajoute ou retire des membres",
            min_values=0,
            max_values=10,
            default_values=default_members,
        )

        self.label = discord.ui.Label(
            text="Membres à ajouter/retirer de la whitelist",
            component=self.user_select,
        )

        self.add_item(self.label)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        added, removed, skipped_self = [], [], False

        for member in self.user_select.values:
            if member.bot:
                continue

            if member.id == self.owner_id:
                skipped_self = True
                continue

            if whitelist.is_in_whitelist(self.owner_id, member.id):
                whitelist.remove_from_whitelist(self.owner_id, member.id)
                await self.channel.set_permissions(member, overwrite=None)
                removed.append(member.mention)
            else:
                whitelist.add_to_whitelist(self.owner_id, member.id)
                await self.channel.set_permissions(member, connect=True)
                added.append(member.mention)

        parts = []
        if added:
            parts.append(f"✅ Ajouté(s) à la whitelist : {', '.join(added)}")
        if removed:
            parts.append(f"❌ Retiré(s) de la whitelist : {', '.join(removed)}")
        if skipped_self:
            parts.append("ℹ️ Tu es déjà propriétaire, pas besoin de t'ajouter à ta propre whitelist.")

        await interaction.followup.send(
            "\n".join(parts) if parts else "Aucune modification.",
            ephemeral=True,
        )


class ControlPanel(discord.ui.View):
    def __init__(self, channel: discord.VoiceChannel, owner_id: int):
        super().__init__(timeout=None)
        self.channel = channel
        self.owner_id = owner_id
        self.whitelist_active = False

    async def check_owner(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "Seul le propriétaire du salon peut faire ça.", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Limiter", style=discord.ButtonStyle.blurple)
    async def limit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_owner(interaction):
            return
        await interaction.response.send_modal(LimitModal(self.channel))

    @discord.ui.button(label="Renommer", style=discord.ButtonStyle.blurple)
    async def rename_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_owner(interaction):
            return
        await interaction.response.send_modal(RenameModal(self.channel))

    @discord.ui.button(label="Ajouter/Retirer de la Whitelist", style=discord.ButtonStyle.blurple)
    async def whitelist_add_member_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_owner(interaction):
            return

        await interaction.response.send_modal(WhitelistModal(self.channel, self.owner_id, interaction.guild))

    @discord.ui.button(label="Passation de Chef", style=discord.ButtonStyle.blurple)
    async def change_owner_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_owner(interaction):
            return
        view = ChangeOwnerView(self.channel, self)
        await interaction.response.send_message(
            "Sélectionne le nouveau chef du salon :", view=view, ephemeral=True
        )
    
    @discord.ui.button(label="Fermer/Ouvrir", style=discord.ButtonStyle.blurple)
    async def close_open_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_owner(interaction):
            return
        overwrite = self.channel.overwrites_for(interaction.guild.default_role)
        if overwrite.connect != False: #Si ouvert
            overwrite.connect = False
            await self.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
            await interaction.response.send_message(f"🔒 {self.channel.name} est maintenant fermé.", ephemeral=True)
        else:
            overwrite.connect = None
            await self.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
            await interaction.response.send_message(f"🔓 {self.channel.name} est maintenant ouvert.", ephemeral=True)
