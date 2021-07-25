from discord.ext import commands, tasks
from discord import Embed
import os
import shutil
import asyncpg
import time

"""
(Automatic) methods to enhance the development flow
Including:
    - automatic pulling and reloading of the cogs folder from branch stable
    - functionality to reload specific / all cogs
    - statistics
    - logging
"""

__authors__ = "Samuel Becker"
__credits__ = ["Samuel Becker"]
__maintainer__ = "Samuel Becker"
__email__ = "beckersamuel9@gmail.com"
__status__ = "WIP"


class logging:
    """
    Log actions, errors etc from modules
    This requires the module to call logging.log(name, message) to work
    """

    def __init__(self, path="data"):
        self.path = path

        if not os.path.isdir(self.path):
            # Log folder does not exist, create it
            os.mkdir(self.path)
        self.logPath = self.path+"/logs"
        if not os.path.isdir(self.logPath):
            os.mkdir(self.logPath)

    def log(self, module: str, message: str):
        if not os.path.isfile(f"{self.logPath}/{module}_log.txt"):
            # Logging file does not exist yet, create it
            open(f"{self.logPath}/{module}_log.txt", "w").close()

        with open(f"{self.logPath}/{module}_log.txt", "a") as f:
            # Write log message in the following format:
            # [YYYY:MM:DD] [HH:mm:SS]: message
            t = time.localtime()
            # Format date to make shure it always has the same length
            date = f"[{t.tm_year}:"
            date = f"{date}{t.tm_mon if t.tm_mon > 9 else '0' + str(t.tm_mon)}:"
            date = f"{date}{t.tm_mday if t.tm_mday > 9 else '0' + str(t.tm_mday)}]"
            # Same with time
            tm = f"[{t.tm_hour if t.tm_hour > 9 else '0' + str(t.tm_hour)}:"
            tm = f"{tm}{t.tm_min if t.tm_min > 9 else '0' + str(t.tm_min)}:"
            tm = f"{tm}{t.tm_sec if t.tm_sec > 9 else '0' + str(t.tm_sec)}]"
            # Now write it
            f.write(f"{date} {tm}: {message}\n")


class Reloader(commands.Cog):
    """
    Reload and update cogs in ./cogs from branch stable
    TODO: Add function to reload specific cog
    """

    def __init__(self, bot):
        self.bot = bot
        self.update.add_exception_type(asyncpg.PostgresConnectionError)
        # self.update.start()

    cmds = (
        'git init',
        'git remote add origin \
        https://github.com/MrEvilOnGitHub/Info2-Bot-Inofficial-.git',
        'git config core.sparseCheckout true',
        'echo "cogs" > .git/info/sparse-checkout',
        'echo "bot-venv" >> .git/info/sparse-checkout',
        'git pull origin stable',
        'rm -rf .git',
        'rsync -u -r --delete -c -b --backup-dir=./../cogs/backup cogs/ ./../cogs',
        'rsync -u -r --delete -c ./bot-venv/ ./../bot-venv'
    )

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} ready")

    def _pullCogs(self):
        if "tmp" in os.listdir():
            shutil.rmtree("./tmp")
        os.mkdir("./tmp")
        os.chdir("./tmp")
        for i in self.cmds:
            if os.system(i) != 0:
                raise os.error("Couldn't sync cogs")
                os.chdir("..")
                shutil.rmtree("./tmp")
                return False
        os.chdir("..")
        shutil.rmtree("./tmp")
        return True

    def cog_unload(self):
        self.update.cancel()

    # Run update every week
    @tasks.loop(hours=24*7)
    async def update(self):
        self._pullCogs()
        await self.reloadAll()

    def reloadAll(self):
        for i in [j[:-3] for j in os.listdir("./cogs") if j[-2:] == "py"]:
            self.bot.logs.log(self.__class__, f"Attempting to reload {i}")
            try:
                self.bot.reload_extension(f"cogs.{i}")
            except Exception as e:
                self.bot.logs.log(
                    self.__class__, f"Failed to reload {i}: {e}")

    @commands.command(hidden=True)
    async def reloadAllCogs(self, context):
        await context.send("Starting reload")
        self.reloadAll()
        await context.send("Finished reloading")

    @commands.command(hidden=True)
    async def reloadCog(self, context, cog: str):
        self.bot.logs.log(self.__class__, f"Attempting to reload {cog}")
        self.bot.logs.log()
        try:
            self.bot.reload_extension(cog)
        except Exception as e:
            self.bot.logs.log("Reloader.reloadCog", e)

    @commands.command(hidden=True)
    async def showActiveCogs(self, context):
        emb = Embed(title="Active Cogs")
        tmp = ""
        for i in self.bot.cogs:
            if len(tmp) > 0:
                tmp = f"{tmp}, {i}"
            else:
                tmp = i
        emb.add_field(name="Cogs", value=tmp)
        await context.reply(embed=emb)


def setup(bot):
    bot.add_cog(Reloader(bot))
