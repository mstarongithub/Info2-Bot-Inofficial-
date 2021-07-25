from discord import Embed
from discord.ext import commands, tasks
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


class Reloader(commands.Cog):
    """
    Reload and update cogs in ./cogs from branch stable
    TODO: Add function to reload specific cog
    """

    def __init__(self, bot):
        self.bot = bot
        self.update.add_exception_type(asyncpg.PostgresConnectionError)
        self.update.start()

    cmds = (
        'git init',
        'git remote add origin \
        https://github.com/MrEvilOnGitHub/Info2-Bot-Inofficial-.git',
        'git config core.sparseCheckout true',
        'echo "cogs" > .git/info/sparse-checkout',
        'echo "bot-venv" >> .git/info/sparse-checkout',
        'git pull origin stable',
        'rm -rf .git',
        'rsync -u -r --delete -c -b --backup-dir=./../cogs/backup \
        cogs/ ./../cogs',
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
            self.bot.reload_extension(f"cogs.{i}")

    @commands.command(hidden=True)
    async def reloadAllCogs(self, context):
        await context.send("Starting reload")
        self.reloadAll()
        await context.send("Finished reloading")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return  # Don't respond to own messages


class logging:
    """
    Log actions, errors etc from modules
    This requires the module to call logging.log(name, message) to work
    """

    def __init__(self, path="./data/logs"):
        self.path = path
        if not os.is_dir(self.path):
            # Log folder does not exist, create it
            os.mkdir(self.path)

    def log(self, module: str, message: str):
        if not os.path.isfile(f"{self.path}/{module}_log.txt"):
            # Logging file does not exist yet, create it
            open(f"{self.path}/{module}_log.txt", "w").close()

        with open(f"{self.path}/{module}_log.txt", "a") as f:
            # Write log message in the following format:
            # [YYYY:MM:DD] [HH:mm:SS]: message
            t = time.localtime()
            f.write(f'[{t.tm_year}:{t.tm_mon}:{t.tm_mday}] \
            [{t.tm_hour}:{t.tm_min}:{t.tm_sec}]: {message}\n')


class statistics:

    """
    Collects statistics on how often something has happened,
    how long the bot has been running, etc
    """

    def __init__(self):
        self._startup = time.time()
        self._funcCounter = {}
        self._io = {
            "read": 0,
            "write": 0
        }

    def registerFunc(self, name):
        """
        Register a function to the counter
        """
        if name not in self.funcCounter:
            self.funcCounter[name] = 0

    def countFunc(self, name: str):
        """
        increase name's counter by 1
        """
        if name not in self._funcCounter:
            # func isn't yet registered in the counter, add it
            self._funcCounter[name] = 0
        self._funcCounter[name] += 1

    def addCounter(self, func):
        """
        Wrapper for automatic counting of calls of func
        """
        # Full func name (class.func) stored in __qualname__
        name = func.__qualname__
        self.registerFunc(name)

        async def wrapper(*args, **kwargs):
            self.countFunc(name)
            await func(*args, **kwargs)

        return wrapper


class statisticsWrapper(commands.Cog):
    """
    Command interface for statistics
    """

    def __init__(self, bot):
        self.bot = bot
        self.startup = time.time()

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Listener: Logs startup once ready
        """
        self.bot.logs.log(self.__class__.__name__, "Started")
        print(f"{self.__class__.__name__} ready")

    @commands.command(name="uptime", description="Get uptime of the bot")
    async def uptime(self, context):
        """
        Send the current uptime
        """
        t = time.gmtime(time.time() - self.bot.startup)
        await context.reply(f'The bot has been running for \
        {t.tm_yday+(t.tm_year-1990)*365} days, {t.tm_hour} hours and \
        {t.tm_min} minutes')

    @commands.command()
    async def listAllFuncCounters(self, context):
        embed = Embed(title="Functions usage",
                      description="List of all functions and how often they've\
                       been used"
                      )
        for key in statistics._funcCounter:
            embed.add_field(
                key, f"Used {statistics()._funcCounter[key]} times")
        await context.send(embed)


def setup(bot):
    bot.add_cog(Reloader(bot))
