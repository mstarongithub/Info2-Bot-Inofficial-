import discord
from discord.ext import commands
import os

import authData

"""
This module's function is to start up the barebones bot
and load in cogs from a subfolder
"""

bot = commands.Bot(command_prefix="i!")

@bot.command()
async def ping(context):
    await context.send("Pong")


if __name__ == '__main__':
    for i in [j[:-3] for j in os.listdir("./cogs") if j[-2:] == "py"]:
        bot.load_extension(f"cogs.{i}")
    bot.run(authData.BOT_TOKEN)
