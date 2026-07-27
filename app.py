import os
import dotenv
import threading
import asyncio

from discordAPI import DiscordAPI
from twitchBot import TwitchBot
from twitchVerify import TwitchLinker
from bot import Bot
from commands.notif_stream import setup as setup_notif_stream
from commands.roles_link import setup as setup_riot_link
from commands.temp_voice import setup as setup_temp_voice
from commands.clear import setup as setup_clear
from commands.help import setup as setup_help
from flaskApp import FlaskApp
from commands.antiSpam import AntiSpam
from commands.update_rank import setup as setup_update_rank

dotenv.load_dotenv()

TOKEN = os.getenv("TOKEN_DISCORD")

if not TOKEN:
    raise ValueError("TOKEN_DISCORD est introuvable dans les variables d'environnement.")

bot = Bot()

discord_api = DiscordAPI()
twitch_bot = TwitchBot()
twitch_linker = TwitchLinker(bot)
flask_app = FlaskApp(twitch_linker)
    
bot.twitch_bot = twitch_bot
bot.discordAPI = discord_api
bot.twitch_linker = twitch_linker

async def main():
    setup_notif_stream(bot, twitch_bot)
    setup_riot_link(bot, discord_api, twitch_linker)
    setup_clear(bot)
    setup_help(bot)
    setup_update_rank(bot)
    await setup_temp_voice(bot)

    bot.AntiSpam = AntiSpam()
    bot.AntiSpam.setup(bot)

    threading.Thread(target=flask_app.run, daemon=True).start()

    async with bot:
        await bot.start(TOKEN)

asyncio.run(main())

