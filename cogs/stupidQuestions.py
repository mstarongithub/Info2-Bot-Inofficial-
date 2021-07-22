"""
Automatic reaction to stupid phrases like if-loop
Those phrases can be created using normal string matching or regular expressions
"""

from discord.ext import commands
import re

class stupidQuestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} ready")

    """
    Format:
        "key1, be it regex or not": "Answer",
        "key2, be it regex or not": "Answer"
    """
    phrases = {
        "if-loop": "While it sometimes may look like it, if constructs are, in fact, not able to construct a loop on their own"
    }

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return # Don't respond to own messages
        final = ""
        for i in self.phrases:
            if re.search(i, message.content):
                # Found a match, add answer to response string
                # Each answer takes it's own line
                final += f"{self.phrases[i]}\n"
        if len(final) > 0:
            await message.reply(final[:-1]) # Cut trailing newline and send it

def setup(bot):
    bot.add_cog(stupidQuestions(bot))
