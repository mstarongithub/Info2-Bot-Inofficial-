import discord
from discord.ext import commands

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
    bot.run(authData.BOT_TOKEN)
