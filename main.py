from discord.ext import commands
import os

import authData
from devTools import logging
from dataHandler import BotData

"""
This module's function is to start up the barebones bot
and load in cogs from a subfolder
"""

__authors__ = "Samuel Becker, Frederik Beimgraben"
__credits__ = ["Samuel Becker", "Frederik Beimgraben"]
__maintainer__ = "Samuel Becker"
__email__ = "beckersamuel9@gmail.com"
__status__ = "WIP"

bot = commands.Bot(command_prefix="i!")
bot.logs = logging()


@bot.command()
async def ping(context):
    await context.send("Pong")


@bot.command()
@commands.is_owner()
async def shutdown(context):
    await context.bot.logout()

if __name__ == '__main__':
    # Entry point
    data = BotData(bot.logs)

    bot.bot_data = data

    for i in [j[:-3] for j in os.listdir("./cogs") if j[-2:] == "py"]:
        # load all .py files in ./cogs as sperate cogs
        try:
            bot.load_extension(f"cogs.{i}")
        except Exception as e:
            # Some error not related to the loading itself occured
            if type(e) not in (commands.ExtensionNotFound,
                               commands.ExtensionAlreadyLoaded,
                               commands.NoEntryPointError,
                               commands.ExtensionFailed):
                bot.logs.log(bot.__class__.__name__, e)
                raise e
            else:
                # Cog failed to load, log it and move on
                bot.logs.log(bot.__class__.__name__, e)
                print(f"Failed to load extension {i}")

    bot.load_extension("devTools")
    bot.run(authData.BOT_TOKEN)
