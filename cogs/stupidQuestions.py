from discord.ext import commands
import re

"""
Automatic reaction to stupid phrases like if-loop
Those phrases can be normal string matching or regular expressions
"""


class stupidQuestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Listener: Logs startup once ready
        """
        self.bot.logs.log(self.__class__.__name__, "Started")
        print(f"{self.__class__.__name__} ready")

    """
    Format:
        "key1, be it regex or not": "Answer",
        "key2, be it regex or not": "Answer"
    """
    phrases = {
        "(?i)if(?:-| )(?:loop|Schleife)": "While it sometimes may look like it, if constructs are, in fact, not able to construct a loop on their own",
        "(?<!GNU)[Ll]inux": "It's GNU/Linux, you buffoon!",
        "(?i)(?:more|not enough|mehr|nicht genug) RAM": "Need more ram? Go to https://www.downloadmoreram.com/download.html"
    }

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Listener: Responds to messages containing certain phrases
        """
        if message.author.id == self.bot.user.id:
            return  # Don't respond to own messages
        final = ""
        for i in self.phrases:
            if re.search(i, message.content):
                # Found a match, add answer to response string
                # Each answer takes it's own line
                final += f"{self.phrases[i]}\n"
        if len(final) > 0:
            self.bot.logs.log(self.__class__.__name__,
                              "Phrase detected, responding")
            await message.reply(final[:-1])  # Cut trailing newline and send it


class dadMode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Listener: Logs startup once ready
        """
        self.bot.logs.log(self.__class__.__name__, "Started")
        print(f"{self.__class__.__name__} ready")

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Listener: Responds to messages containing "I'm x" or "I am x" with
        "Hi x, I'm dad"
        """
        if message.author.id == self.bot.user.id:
            return  # Don't respond to own messages
        # Match any string with the syntax of I'm x | I am x
        match = re.search(r".?(?:I'm|I am) (\b.*\b)", message.content)
        if match:
            self.bot.logs.log(self.__class__.__name__, "Sending dad message")
            await message.reply(f"Hi {match.group(1)}, I'm Info2-Bot!")


def setup(bot):
    bot.add_cog(stupidQuestions(bot))
    bot.add_cog(dadMode(bot))
