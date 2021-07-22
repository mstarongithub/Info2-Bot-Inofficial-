"""
Automatic reaction to stupid phrases like if-loop
"""

from discord.ext import commands

class example(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    """
    Format:
        "keyInTest": "Answer"
    """
    phrases = {
        "if-loop": "While it sometimes may look like it, if constructs are, in fact, not able to construct a loop on their own"
    }

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return
        for i in self.phrases:
            if i in message.content:
                await message.reply(self.phrases[i])

def setup(bot):
    bot.add_cog(example(bot))
