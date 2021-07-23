"""
(Automatic) methods to enhance the development flow
Including:
    - automatic pulling and reloading of the cogs folder from a known stable branch
    - functionality to reload specific / all cogs
    - statistics
    - logging
"""

"""
Notes:
    Download single folder using git:
    Setup:
        - mkdir newFolder
        - git init
        - git remote add origin https://github.com/MrEvilOnGitHub/Info2-Bot-Inofficial-.git
        - git config core.sparseCheckout true
        - echo "cogs" > .git/info/sparse-checkout
        - git pull origin branch
"""

from discord.ext import commands, tasks

class Reloader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} ready")

    @commands.command(description="description")
    async def ex(self, context):
        await context.send("Example")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return # Don't respond to own messages

def setup(bot):
    bot.add_cog(Reloader(bot))
