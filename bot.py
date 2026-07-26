import asyncio
import discord
from discord.ext import commands
import time
import utils.jsonStorage
import antiSpam

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.messages = True

        super().__init__(command_prefix="!", intents=intents)

        self.background_task = None
        self.twitch_bot = None
        self.link_view_manager = None
        self.anti_spam = antiSpam.AntiSpam()


    async def setup_hook(self):
        synced = await self.tree.sync()
        print(f"INFO - Synchronized commands: {[cmd.name for cmd in synced]}")

        if self.link_view_manager is not None:
            await self.link_view_manager.init()

    async def on_ready(self):
        print(f"INFO - Connected as {self.user}")

        if self.twitch_bot is not None:
            self.twitch_bot.init_status_streams()

        if self.background_task is None or self.background_task.done():
            self.background_task = asyncio.create_task(self.stream_check_loop())
            print("INFO - Background task for stream checking started.")
            print(self.twitch_bot)
    
    async def on_message(self, message):
        if message.author.bot:
            return

        is_spam = self.anti_spam.on_message(message)

        if is_spam:
            for msg in self.anti_spam.get_user_messages(message.author.id):
                if time.time() - msg["timestamp"] < 15:
                    try:
                        await msg["message"].delete()
                    except discord.NotFound:
                        pass
                    except discord.Forbidden:
                        pass
                    except discord.HTTPException:
                        pass
            
            await msg["message"].author.kick(reason="Spam détecté. Kick automatique par le bot.")

            data = utils.jsonStorage.load_data()
            admin_channel_id = data.get("anti_spam_admin_channel_id")
            if admin_channel_id:
                admin_channel = self.get_channel(admin_channel_id)
                if admin_channel:
                    await admin_channel.send(f"⚠️ {message.author.mention} a été expulsé pour spam.")

        await self.process_commands(message)

    async def stream_check_loop(self):
        while not self.is_closed():
            print("INFO - Checking streams...aa")
            self.twitch_bot.check_streams_pings(self)
            await asyncio.sleep(60)
        print("INFO - Stream check loop has been stopped because the bot is closed.")