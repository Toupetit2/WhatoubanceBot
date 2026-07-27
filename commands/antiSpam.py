from collections import defaultdict, deque
import time
import discord
from discord import app_commands
import utils.jsonStorage

class AntiSpam:
    def __init__(self):
        self.messages = defaultdict(lambda: deque(maxlen=20))

    def on_message(self, message):
        user_id = str(message.author.id)
        now = time.time()

        self.messages[user_id].append({
            "channel_id": message.channel.id,
            "message": message,
            "content": message.content,
            "timestamp": now
        })

        return self.is_spamming(message.author.id)

    def is_spamming(self, user_id):
        now = time.time()

        user_messages = self.messages.get(str(user_id), [])

        recent = [msg for msg in user_messages if now - msg["timestamp"] <= 12]

        contents = [msg["content"] for msg in recent]
        if contents:
            most_common = max(set(contents), key=contents.count)
            if contents.count(most_common) >= 3: 
                channels = {msg["channel_id"] for msg in recent}
                if len(channels) >= 3:
                    return True
        
        return False

    def get_user_messages(self, user_id):
        return list(self.messages.get(str(user_id), []))


    def setup(self, bot):
        @app_commands.guild_only()
        @app_commands.default_permissions(administrator=True)
        @bot.tree.command(name="setup_anti_spam", description="Définir le salon admin pour l'anti-spam")
        async def anti_spam_setup_command(interaction: discord.Interaction, channel: discord.TextChannel):
            data = utils.jsonStorage.load_data()
            data["anti_spam_admin_channel_id"] = channel.id
            utils.jsonStorage.save_data(data)

            await interaction.response.send_message(
                f"✅ Salon admin pour l'anti-spam défini sur {channel.mention} !",
                ephemeral=True
            )
