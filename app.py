import os
import dotenv
import threading
import asyncio
from bot import Bot
from flaskApp import FlaskApp
from commands.antiSpam import AntiSpam
from bot_setup import bot_setup


dotenv.load_dotenv()

TOKEN = os.getenv("TOKEN_DISCORD")

if not TOKEN:
    raise ValueError("TOKEN_DISCORD est introuvable dans les variables d'environnement.")

bot = Bot()

flask_app = FlaskApp(bot.twitch_linker)
    
async def main():
    await bot_setup(bot)

    threading.Thread(target=flask_app.run, daemon=True).start()

    async with bot:
        await bot.start(TOKEN)

asyncio.run(main())

