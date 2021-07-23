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
    Pull:
        - git pull origin branch

    Method:
        - Create tmp folder
        - follow setup steps
        - overwrite files in cog with files in tmp/cog
        - delete tmp folder
"""

from discord.ext import commands, tasks

class Reloader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    cmds = (
        'mkdir tmp',
        'cd tmp',
        'git init',
        'git remote add origin https://github.com/MrEvilOnGitHub/Info2-Bot-Inofficial-.git',
        'git config core.sparseCheckout true',
        'echo "cogs" > .git/info/sparse-checkout',
        'echo "bot-venv" >> .git/info/sparse-checkout',
        'git pull origin stable',
        'rm -rf .git',
        'rsync -u -r --delete -c -b --backup-dir=./../cogs/backup cogs/ ./../cogs',
        'rsync -u -r --delete -c ./bot-venv/ ./../bot-venv',
        'cd ..',
        'rm -rf tmp'
    )


    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} ready")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return # Don't respond to own messages

def setup(bot):
    bot.add_cog(Reloader(bot))
