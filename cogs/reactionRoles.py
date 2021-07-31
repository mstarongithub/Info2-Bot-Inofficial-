from discord.ext import commands

"""
Create Reaction-Role Messages
"""


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = bot.bot_data

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Listener: Logs startup once ready
        """
        self.bot.logs.log(self.__class__.__name__, "Started")
        print(f"{self.__class__.__name__} ready")

    @commands.command()
    async def rmessage(self, context):
        self.bot.logs.log(self.__class__, "Reation Role Message created")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return  # Don't respond to own messages


def setup(bot):
    bot.add_cog(ReactionRoles(bot))
