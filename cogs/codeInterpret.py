"""
Features regarding code interpretation and execution
"""

import discord
from discord.ext import commands
from discord.ext.commands.core import command

from pistonapi import PistonAPI

__authors__    = "Frederik Beimgraben"
__credits__    = ["Frederik Beimgraben"]
__maintainer__ = "Frederik Beimgraben"
__email__      = "beimgraben8@gmail.com"
__status__     = "WIP"

class ExecCode(commands.Cog):
    """
    Execute codeblocks and respond with their output
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

    # Error indicating keywords (must be lowercase)
    errors = [
        'error',
        'exception',
        'segmentationfault',
        'invalid'
    ]

    def __contains_error(self, string):
        """
        Check if `string` contains any keyword within `self.errors`
        """

        for e in self.errors:
            if e in string.lower():
                return True
        return False

    def __make_embed(self, body, lang, version):
        """
        Create an embed containing the response `body` as well as the used
        interpreter `lang` and it´s `version`.

        Embed color:
        - `0xff2300` (Red) if an error occured during execution.
        - `0x6fbbd3` (Blue) otherwise
        """

        err = self.__contains_error(body)
        col = 0xff2300 if err else 0x6fbbd3
        embed = discord.Embed(
            title=f'Result using `{lang} ({version})`',
            color=col
        )
        embed.add_field(name='Command Line Output', value=body)
        return embed

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Listener: Prints class name to stdout once ready
        """
        print(f"{self.__class__.__name__} ready")

    @commands.Cog.listener()
    async def on_message(self, context):
        """
        Listener: Responds to any codeblocks with a supported language tag
        """

        if message.author.id == self.bot.user.id:
            return # Don't respond to own messages

        message = context.content

        if message[:3] == '```' and message[-3:] == '```':
            # Message is a codeblock
            lang = message.split('\n')[0][3:]
            code = message.replace(f'```{lang}\n', '')[:-3]
            if lang in self.langs:
                # Language is supported
                body = (
                    '```\n' +
                    self.api.execute(
                        language=lang,
                        version=self.vers[lang],
                        code=code
                     ) +
                    '```'
                )
                await context.channel.send(
                    embed=self.__make_embed(
                        body,
                        lang,
                        self.vers[lang]
                    )
                )


def setup(bot):
    piston = PistonAPI()

    bot.add_cog(ExecCode(bot, piston))
