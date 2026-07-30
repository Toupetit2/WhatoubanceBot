import discord
from discord import app_commands
from utils.jsonStorage import load_data, save_data

class DeleteRankView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="❌ Supprime ton rank", style=discord.ButtonStyle.gray, custom_id="DeleteRankView")
    async def delete_rank_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            data = load_data()
            user_key = str(interaction.user.id)

            if "riot_links" not in data or user_key not in data["riot_links"]:
                await interaction.response.send_message("Aucune donnée de rank trouvée pour toi.", ephemeral=True)
                return

            current_rank = data["riot_links"][user_key].get("tft_rank")
            del data["riot_links"][user_key]
            save_data(data)

            if current_rank:
                role_key = f"tft_rank_{current_rank}_role_id"
                role_id = data.get(role_key)
                if role_id:
                    role = interaction.guild.get_role(role_id)
                    if role and role in interaction.user.roles:
                        await interaction.user.remove_roles(role, reason="Suppression des données de rank via bouton")

            await interaction.response.send_message("Toutes les informations collectées ont été supprimées, et ton rôle de rank a été retiré.", ephemeral=True)

        except Exception as e:
            print(f"[DeleteRankView] Erreur : {e}")
            import traceback
            traceback.print_exc()
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)

def setup(bot):
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @bot.tree.command(name="setup_delete_rank_button", description="Envoie un bouton pour supprimer son compte riot")
    async def delete_rank_command(interaction: discord.Interaction):

        view = DeleteRankView()

        await interaction.channel.send(view=view)
        await interaction.response.send_message("Bouton envoyé !", ephemeral=True)
