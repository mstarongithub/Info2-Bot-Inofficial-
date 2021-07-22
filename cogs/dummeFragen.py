"""
Automatic reaction to stupid phrases like if-loop
"""

from discord.ext import commands
import re

class example(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} ready")

    """
    Format:
        ("key, be it regex or not", "Answer")
    """
    phrases = {
        "if-loop": "While it sometimes may look like it, if constructs are, in fact, not able to construct a loop on their own"
    }

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return
        final = ""
        for i in self.phrases:
            if re.search(i, message.content):
                final += f"{self.phrases[i]}\n"
        if len(final) > 0:
            await message.reply(final[:-1])

def setup(bot):
    bot.add_cog(example(bot))
