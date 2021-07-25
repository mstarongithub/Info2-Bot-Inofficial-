from discord.ext import commands
from discord import Embed
import time


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
        x = f'The bot has been running for {t.tm_yday+(t.tm_year-1990)*365} days, {t.tm_hour} hours and {t.tm_min} minutes'
        await context.reply(x)

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
