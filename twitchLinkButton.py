import discord
from utils.jsonStorage import load_data, save_data
from discordAPI import DiscordAPI
class VerifyView(discord.ui.View):
    def __init__(self, discordAPI):
        super().__init__(timeout=None)
        self.discordAPI = discordAPI

    @discord.ui.button(
        label="✅ J'ai vérifié mon compte Twitch",
        style=discord.ButtonStyle.green,
        custom_id="twitch_verify_button"
    )
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()

        user_id = str(interaction.user.id)
        temp_accounts = data.get("temp_linked_accounts", {})

        if user_id not in temp_accounts:
            await interaction.response.send_message(
                "⚠️ Aucun compte Twitch en attente de vérification trouvé pour ton compte Discord. Assure-toi d'avoir cliqué sur le bouton de liaison Twitch et d'avoir vérifié ton compte Twitch avant de cliquer ici.",
                ephemeral=True
            )
            return

        twitch_name = temp_accounts[user_id]
        is_wtb_account = twitch_name.lower().startswith("wtb")

        if is_wtb_account:
            await self.discordAPI.give_role(
                interaction.client,
                data["guild_id"],
                interaction.user.id,
                data["wtb_twitch_role_id"]
            )

        del data["temp_linked_accounts"][user_id]

        save_data(data)

        if is_wtb_account:
            await interaction.response.send_message(
                "✅ Compte Twitch vérifié ! Tu as reçu le rôle de WTB_Twitch !",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "✅ Compte Twitch vérifié ! Ton pseudo ne commence pas par WTB, tu ne recevras donc pas le rôle.",
                ephemeral=True
            )
class TwitchLinkView(discord.ui.View):
    def __init__(self, twitch_linker, discordAPI):
        super().__init__(timeout=None)
        self.twitch_linker = twitch_linker
        self.discordAPI = discordAPI

    @discord.ui.button(label="🔗 Lier mon Twitch", style=discord.ButtonStyle.blurple, custom_id="twitch_link_button")
    async def link_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        discord_id = str(interaction.user.id)

        auth_url = self.twitch_linker.get_auth_url(discord_id)

        await interaction.response.send_message(
            f"👉 Clique ici pour lier ton Twitch :\n{auth_url}",view=VerifyView(self.discordAPI),
            ephemeral=True
        )

