import discord
from discord import app_commands
from utils.jsonStorage import load_data, save_data
import tftAPI
import rate_limiter
async def update_rank(interaction: discord.Interaction, member: discord.Member):
    data = load_data()
    member_id = str(member.id)

    if member_id not in data["riot_links"]:
        return f"<@{member.id}> n'a pas lié son compte riot."

    old_rank = data["riot_links"][member_id]["tft_rank"]
    puuid = data["riot_links"][member_id]["puuid"]
    cpid = data["riot_links"][member_id]["cpid"]

    current_rank = tftAPI.get_tft_rank(puuid, cpid)

    role_id = data.get(f"tft_rank_{old_rank}_role_id")
    role = interaction.guild.get_role(role_id)

    if current_rank != old_rank:
        try:
            await member.add_roles(role)
        except discord.Forbidden:
            return "Le rôle est trop haut dans la hiérarchie."
        except discord.HTTPException as e:
            return f"Erreur lors de l'ajout du rôle : {e}"

        return f"<@{member.id}> a eu son rôle mis a jour !"
    else:
        if role not in member.roles: 
            try:
                await member.add_roles(role)
            except discord.Forbidden:
                return "Le rôle est trop haut dans la hiérarchie."
            except discord.HTTPException as e:
                return f"Erreur lors de l'ajout du rôle : {e}"
            return f"<@{member.id}> a eu son rôle mis a jour !"

        return f"<@{member.id}> avait déjà le bon rôle."

class UpdateRankView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔄 Update ton rank", style=discord.ButtonStyle.primary, custom_id="UpdateRankView")
    async def rename_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        message = await update_rank(interaction, interaction.user)
        
        await interaction.response.send_message(message, ephemeral=True)

def setup(bot):
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @bot.tree.command(name="update_rank", description="Met a jour le rank du membre choisi")
    @app_commands.describe(member="Le membre qui va avoir son rank mis a jour")
    async def update_rank_command(interaction: discord.Interaction, member: discord.Member):

        message = await update_rank(interaction, member)

        await interaction.response.send_message(message, ephemeral=True)


    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @bot.tree.command(name="setup_update_rank_button", description="Envoie un bouton pour pouvoir mettre a jour son rank")
    async def setup_update_rank_command(interaction: discord.Interaction):

        view = UpdateRankView()

        await interaction.response.send_message("", view=view)

    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @bot.tree.command(name="update_rank_everyone", description="Met a jour le rank de tout le serveur")
    async def update_rank_everyone_command(interaction: discord.Interaction):

        members = interaction.guild.members

        for member in members:
            await update_rank(interaction, member)
            

        await interaction.response.send_message("")


