import os
import dotenv
import discord
from discord import app_commands
from discord.ext import commands

dotenv.load_dotenv()
dotenv_file = dotenv.find_dotenv()

TOKEN = os.getenv("TOKEN_DISCORD")

class DiscordAPI:

    async def send_message(self, bot, channel_id, message=None, embed=None, view=None):
        # channel_id -> int, the id of the channel to send the message in
        # message -> str, the message to send
        # embed -> discord.Embed, the embed to send
        # view -> discord.ui.View, the view to send

        channel = bot.get_channel(channel_id)

        if channel:
            return await channel.send(content=message, embed=embed, view=view)
    
    async def send_dm(self, bot, user_id, message):
        # user_id -> int, the id of the user to send the dm to
        # message -> str, the message to send

        user = await bot.fetch_user(user_id)

        if user:
            await user.send(content=message)
    
    async def give_role(self, bot, guild_id, user_id, role_id):
        # guild_id -> int, the id of the guild where the role is
        # user_id -> int, the id of the user to give the role to
        # role_id -> int, the id of the role to give

        guild = bot.get_guild(guild_id)

        if guild:
            member = guild.get_member(user_id)
            role = guild.get_role(role_id)

            if member and role:
                await member.add_roles(role)

        print(f"Debug - Given role {role_id} to user {user_id} in guild {guild_id}", flush=True)
