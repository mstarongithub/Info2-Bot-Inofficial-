"""
Features regarding code interpretation and execution
"""

from discord.ext import commands
from discord.ext.commands.core import command

from pistonapi import PistonAPI

class SyntaxCheck(commands.Cog):
    """
    Check the syntax of code blocks
    """

    def __init__(self, bot, piston_api):
        self.langs = [
                key for key in piston_api.languages
            ]
        self.api = piston_api
        self.bot = bot

class ExecCode(commands.Cog):
    """
    Execute code and display it´s output
    """

    def __init__(self, bot, piston_api):
        langs = piston_api.languages
        self.vers  = {
                key : langs[key]['version'] for key in langs
            }
        self.langs = [
                key for key in langs
            ]
        self.api = piston_api
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def execute(self, context):
        message = context.content
        if context.content[:3] == "```":
            lang = message.split('\n')[0][3:]
            code = message.replace(f'```{lang}\n', '')[:-3]
            if lang in self.langs:
                await context.channel.send(
                    'Output:```\n' +
                    self.api.execute(
                        language=lang, version=self.vers[lang], code=code) +
                    '```'
                )


def setup(bot):
    piston = PistonAPI()

    bot.add_cog(SyntaxCheck(bot, piston))
    bot.add_cog(ExecCode(bot, piston))