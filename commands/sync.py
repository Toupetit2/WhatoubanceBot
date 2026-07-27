import discord
from discord import app_commands
from discord.ext import commands

def setup(bot):
    @bot.command()
    @commands.is_owner()
    async def sync(ctx):
        synced = await bot.tree.sync()
        await ctx.send(f"{len(synced)} commande(s) synchronisée(s).")