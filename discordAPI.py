import os
import asyncio
import dotenv
import discord
from discord import app_commands
from discord.ext import commands

dotenv.load_dotenv()
dotenv_file = dotenv.find_dotenv()

TOKEN = os.getenv("TOKEN_DISCORD")

class DiscordAPI:

    async def send_message(self, bot, channel_id, message=None, embed=None, view=None, delete_after=0):
        # channel_id -> int, the id of the channel to send the message in
        # message -> str, the message to send
        # embed -> discord.Embed, the embed to send
        # view -> discord.ui.View, the view to send

        channel = bot.get_channel(channel_id)

        if channel:
            return await channel.send(content=message, embed=embed, view=view, delete_after=delete_after)
    
    async def send_dm(self, bot, user_id, message):
        # user_id -> int, the id of the user to send the dm to
        # message -> str, the message to send

        user = await bot.fetch_user(user_id)

        if user:
            await user.send(content=message)
    
    async def give_role(self, bot, guild_id, user_id, role_id, max_retries=3):
        # guild_id -> int, the id of the guild where the role is
        # user_id -> int, the id of the user to give the role to
        # role_id -> int, the id of the role to give

        guild = bot.get_guild(guild_id)
        if not guild:
            raise ValueError(f"Guild {guild_id} introuvable")

        role = guild.get_role(role_id)
        if role is None:
            raise ValueError(f"Rôle {role_id} introuvable")

        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                member = guild.get_member(user_id) or await guild.fetch_member(user_id)
                await member.add_roles(role)
                return
            except discord.NotFound as e:
                last_error = e
            except discord.HTTPException as e:
                last_error = e
                if attempt < max_retries:
                    await asyncio.sleep(5 * attempt)

        raise last_error

    async def remove_role(self, bot, guild_id, user_id, role_id):
        # guild_id -> int, the id of the guild where the role is
        # user_id -> int, the id of the user to remove the role from
        # role_id -> int, the id of the role to remove

        guild = bot.get_guild(guild_id)

        if guild:
            member = guild.get_member(user_id)
            role = guild.get_role(role_id)

            if member and role:
                await member.remove_roles(role)
