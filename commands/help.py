import discord
from discord import app_commands
from discord.ext import commands

def setup(bot):
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @bot.tree.command(name="help", description="Envoie la liste des commandes")
    async def help_command(interaction: discord.Interaction):
        await interaction.response.send_message(
                    """## Commandes Admin
### Commandes Twitch Notifier
**/add_stream**  username channel message(optional)   - ajoute un stream notifier
**/remove_stream**  username                                                - supprime le stream notifier de "username"
**/modify_stream_message** username message             - change le message d'annonce du stream notifier pour "username"
**/list_streams **                                                                           - donne la liste des notifier et leurs messages
### Commandes TempVoice
**/setup_temp_voice** category                                             - Rajoute un salon "Créer un salon" dans la catégorie
### Commandes Rôles
**/setup_link wtb_role**                                                            - Envoie le message de link riot et twitch, donne le role wtb_role après la vérification twitch (si wtb tag)
**/setup_rank_roles** iron bronze silver gold plat...         - Permet de donner les bons roles quand on link avec riot
**/update_rank** member                                                        - Met a jour le rank du membre si il a lié son compte
**/setup_update_rank_button**                                            - Envoie un bouton pour update son rank
**/update_rank_everyone**                                                      - Met a jour le rank de tous les membres 
### Commandes AntiSpam
**/setup_anti_spam** channel                                                 - Envoie des messages d'annonce dans le channel en cas de ban avec l'antispam
**/clear** nombre                                                                          -Supprime les X derniers messages dans le channel""",
                    ephemeral=True
        )