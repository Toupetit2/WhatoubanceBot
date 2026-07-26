import os
import dotenv
import threading
import asyncio

from discordAPI import DiscordAPI
from twitchBot import TwitchBot
from twitchVerify import TwitchLinker
from twitchLinkButton import TwitchLinkViewManager
from bot import Bot
from commands.notif_stream import setup as setup_notif_stream
from commands.twitch_link import setup as setup_twitch_link
from commands.riot_link import setup as setup_riot_link
from commands.temp_voice import setup as setup_temp_voice
from flaskApp import FlaskApp
from antiSpam import AntiSpam

dotenv.load_dotenv()

TOKEN = os.getenv("TOKEN_DISCORD")

if not TOKEN:
    raise ValueError("TOKEN_DISCORD est introuvable dans les variables d'environnement.")

bot = Bot()

discord_api = DiscordAPI()
twitch_bot = TwitchBot()
twitch_linker = TwitchLinker(bot)
flask_app = FlaskApp(twitch_linker)
twitch_link_view_manager = TwitchLinkViewManager(bot, twitch_linker, discord_api)
    
bot.twitch_bot = twitch_bot

async def main():
    setup_notif_stream(bot, twitch_bot)
    setup_twitch_link(bot, twitch_linker, discord_api)
    setup_riot_link(bot, discord_api)
    await setup_temp_voice(bot)

    bot.AntiSpam = AntiSpam()
    bot.AntiSpam.setup(bot)

    threading.Thread(target=flask_app.run, daemon=True).start()

    async with bot:
        await bot.start(TOKEN)

asyncio.run(main())

