from discord.ext import commands
import praw

"""
Description
"""


class memes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reddit = praw.Reddit(
            client_id=bot.auth.reddit.client_id,
            client_secret=bot.auth.reddit.client_secret,
            user_agent=bot.auth.reddit.user_agent
        )

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Listener: Logs startup once ready
        """
        self.bot.logs.log(self.__class__.__name__, "Started")


def setup(bot):
    bot.add_cog(memes(bot))
