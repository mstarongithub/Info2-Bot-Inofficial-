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

    def __init__(self, path: str = "data") -> None:
        self.path = path

        if not os.path.isdir(self.path):
            # Data folder doesn't exist, create it
            os.mkdir(self.path)
        self.log_path = self.path+"/logs"
        if not os.path.isdir(self.log_path):
            # Logs folder doesn't exist inside data, create it
            os.mkdir(self.log_path)

    def log(self, module: str, message: str) -> None:
        """
        Saves message in file path/logs/module_log.txt
        Save format: [YYYY:MM:DD] [HH:mm:SS]: message
        """
        if not os.path.isfile(f"{self.log_path}/{module}_log.txt"):
            # Logging file does not exist yet, create it
            open(f"{self.log_path}/{module}_log.txt", "w").close()

        with open(f"{self.log_path}/{module}_log.txt", "a") as f:
            t = time.localtime()
            # Format date to make shure it always has the same length
            date = f"[{t.tm_year}:"
            date = f"{date}{t.tm_mon if t.tm_mon > 9 else f'0{t.tm_mon}'}:"
            date = f"{date}{t.tm_mday if t.tm_mday > 9 else  f'0{t.tm_mday}'}]"
            # Same with time
            tm = f"[{t.tm_hour if t.tm_hour > 9 else '0' + str(t.tm_hour)}:"
            tm = f"{tm}{t.tm_min if t.tm_min > 9 else '0' + str(t.tm_min)}:"
            tm = f"{tm}{t.tm_sec if t.tm_sec > 9 else '0' + str(t.tm_sec)}]"
            # Now write it
            f.write(f"{date} {tm}: {message}\n")


class reloader(commands.Cog):
    """
    Reload and update cogs in ./cogs from branch stable
    Automatic reloading is currently disabled, uncomment line 72 to enable
    """

    def __init__(self, bot):
        self.bot = bot
        self.update.add_exception_type(asyncpg.PostgresConnectionError)
        # self.update.start()

    # Set of commands used to update the cogs folder from the master branch
    lnk = "https://github.com/MrEvilOnGitHub/Info2-Bot-Inofficial-.git"
    cmds = (
        'git init',
        f'git remote add origin {lnk}',
        'git config core.sparseCheckout true',
        'echo "cogs" > .git/info/sparse-checkout',
        'echo "bot-venv" >> .git/info/sparse-checkout',
        'git pull origin master',
        'rm -rf .git',
        'rsync -u -r --delete -c cogs/ ./../cogs',
        'rsync -u -r --delete -c ./bot-venv/ ./../bot-venv'
    )

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Listener: Logs startup once ready
        """
        self.bot.logs.log(self.__class__.__name__, "Started")
        print(f"{self.__class__.__name__} ready")

    def __pull_cogs(self) -> bool:
        """
        Pull the ./cogs from the master branch
        """
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
        """
        Cancel the updates when this cog gets unloaded
        """
        self.update.cancel()

    # Run update every week
    @tasks.loop(hours=24*7)
    async def update(self):
        """
        Repeated task: Update and reload the ./cogs folder every week
        """
        self.__pull_cogs()
        await self.reload_all()

    def reload_all(self) -> None:
        """
        Reload all extensions inside ./cogs
        """
        for i in [j[:-3] for j in os.listdir("./cogs") if j[-2:] == "py"]:
            self.bot.logs.log(self.__class__, f"Attempting to reload {i}")
            try:
                self.bot.reload_extension(f"cogs.{i}")
            except Exception as e:
                self.bot.logs.log(
                    self.__class__.__name__, f"Failed to reload {i}: {e}")

    @commands.command(hidden=True)
    @commands.has_guild_permissions(administrator=True)
    async def reload_all_cogs(self, context: commands.context.Context):
        """
        Command: Reload all cogs in ./cogs
        """
        await context.send("Starting reload")
        self.reload_all()
        await context.send("Finished reloading")

    @commands.command(hidden=True)
    @commands.has_guild_permissions(administrator=True)
    async def reload_cog(self, context: commands.context.Context, cog: str):
        """
        Reload extension cog.
        """
        self.bot.logs.log(self.__class__, f"Attempting to reload {cog}")
        self.bot.logs.log()
        try:
            self.bot.reload_extension(cog)
        except Exception as e:
            await context.send("Failed to reload cog")
            self.bot.logs.log(self.__class__.__name__, e)

    @commands.command(hidden=True)
    @commands.has_guild_permissions(administrator=True)
    async def show_active_cogs(self, context: commands.context.Context):
        """
        Send an Embed that lists all active cogs
        """
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
    bot.add_cog(reloader(bot))
