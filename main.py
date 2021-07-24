"""
This module's function is to start up the barebones bot
and load in cogs from a subfolder
"""

import discord
from discord.ext import commands
import os

import authData
from devTools import logging

__authors__    = "Samuel Becker"
__credits__    = ["Samuel Becker"]
__maintainer__ = "Samuel Becker"
__email__      = ""
__status__     = "WIP"

bot = commands.Bot(command_prefix="i!")
bot.logs = logging()

@bot.command()
async def ping(context):
    await context.send("Pong")


if __name__ == '__main__':
    for i in [j[:-3] for j in os.listdir("./cogs") if j[-2:] == "py"]:
        bot.load_extension(f"cogs.{i}")
    bot.load_extension("devTools")
    bot.run(authData.BOT_TOKEN)
