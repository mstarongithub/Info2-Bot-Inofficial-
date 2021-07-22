"""
Features regarding code interpretation and execution
"""

import discord
from discord.ext import commands
from discord.ext.commands.core import command

from pistonapi import PistonAPI

errors = [
    'error',
    'exception',
    'segmentationfault',
    'invalid'
]

def contains_error(string):
    for e in errors:
        if e in string.lower(): 
            return True
    return False

def make_embed(body, lang, version):
    err = contains_error(body)
    col = 0xff2300 if err else 0x6fbbd3
    embed = discord.Embed(
        title=f'Result using `{lang} ({version})`', 
        color=col
    )
    embed.add_field(name='Command Line Output', value=body)
    return embed

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
                    embed=make_embed(
                        '```\n' +
                        self.api.execute(
                            language=lang, 
                            version=self.vers[lang], 
                            code=code
                        ) +
                        '```',
                        lang,
                        self.vers[lang]
                    )
                )


def setup(bot):
    piston = PistonAPI()

    bot.add_cog(ExecCode(bot, piston))