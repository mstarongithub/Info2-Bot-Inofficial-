"""
This module's function is to start up the barebones bot
and load in cogs from a subfolder
"""

import discord
from discord.ext import commands
import os

import authData

from dataHandler import BotData

__authors__    = "Samuel Becker, Frederik Beimgraben"
__credits__    = ["Samuel Becker", "Frederik Beimgraben"]
__maintainer__ = "Samuel Becker"
__email__      = ""
__status__     = "WIP"

bot = commands.Bot(command_prefix="i!")

@bot.command()
async def ping(context):
    await context.send("Pong")

@bot.command()
@commands.is_owner()
async def shutdown(context):
    await context.bot.logout()

if __name__ == '__main__':
    data = BotData()

    bot.bot_data = data

    bot.bot_data["guilds.test"] = 5

    del bot.bot_data["guilds"]

    for i in [j[:-3] for j in os.listdir("./cogs") if j[-2:] == "py"]:
        bot.load_extension(f"cogs.{i}")
    bot.run(authData.BOT_TOKEN)
