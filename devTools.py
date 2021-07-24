"""
(Automatic) methods to enhance the development flow
Including:
    - automatic pulling and reloading of the cogs folder from a known stable branch
    - functionality to reload specific / all cogs
    - statistics
    - logging
"""


from discord.ext import commands, tasks
import os, shutil, asyncpg

class Reloader(commands.Cog):
    """
    Provide functionality for reloading cogs in ./cogs and updating them from branch stable
    TODO: Add function to reload specific cog
    """
    def __init__(self, bot):
        self.bot = bot
        self.update.add_exception_type(asyncpg.PostgresConnectionError)
        self.update.start()

    cmds = (
        'git init',
        'git remote add origin https://github.com/MrEvilOnGitHub/Info2-Bot-Inofficial-.git',
        'git config core.sparseCheckout true',
        'echo "cogs" > .git/info/sparse-checkout',
        'echo "bot-venv" >> .git/info/sparse-checkout',
        'git pull origin stable',
        'rm -rf .git',
        'rsync -u -r --delete -c -b --backup-dir=./../cogs/backup cogs/ ./../cogs',
        'rsync -u -r --delete -c ./bot-venv/ ./../bot-venv'
#       'cd ..',
#    'rm -rf tmp'
    )

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
    async def on_ready(self):
        print(f"{self.__class__.__name__} ready")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return # Don't respond to own messages

def setup(bot):
    bot.add_cog(Reloader(bot))
