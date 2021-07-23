"""
Command generated surveys
"""

import discord
from discord.ext import commands
import time
import ast

__authors__    = "Frederik Beimgraben"
__credits__    = ["Frederik Beimgraben"]
__maintainer__ = "Frederik Beimgraben"
__email__      = "beimgraben8@gmail.com"
__status__     = "WIP"

class SurveysReact(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} ready")

    __numbers = [
        "{}\N{COMBINING ENCLOSING KEYCAP}".format(num) for num in range(1, 10)
    ]

    def __get_react(self, i=0):
        assert i < 9
        return f'{self.__numbers[i]}'

    def __make_embed(self, name, desc, untl, options):
        """
        Create an embed containing the response `body` as well as the used
        interpreter `lang` and it´s `version`.

        Embed color:
        - `0xff2300` (Red) if an error occured during execution.
        - `0x6fbbd3` (Blue) otherwise
        """

        body = f"*{desc}*\n"

        for o in range(len(options)):
            body += f'\n{self.__get_react(o)}:  **{options[o]}**'

        body += f'\n\n**Vote until {untl}**'

        embed = discord.Embed(
            title=f'New Survey: {name}',
            color=0x6ffbaa
        )

        embed.add_field(name='Description: ', value=body)
        return embed

    @commands.command(
        description="*survey* \"name\" \"description\" \"until\" \"opt1\" ...")
    async def survey(self, context, *args):
        if len(args) >= 3:
            name = args[0]
            desc = args[1]
            untl = args[2]
            opts = args[3:] if len(args) > 3 else ["Ja", "Nein"]

            guild_id = context.message.guild.id

            message = await context.send(
                embed=self.__make_embed(name, desc, untl, opts)
            )

            for o in range(len(opts)):
                await message.add_reaction(self.__get_react(i=o))

            path = f"surveys.{message.id}"

            self.bot.bot_data[f'{path}.name']        = name
            self.bot.bot_data[f'{path}.description'] = desc
            self.bot.bot_data[f'{path}.until']       = untl
            self.bot.bot_data[f'{path}.options']     = opts
            

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, _):
        if reaction.me:
            return # Don't respond to own messages

        if reaction.message.id in self.bot.bot_data['surveys']:
            print("Something Happened!")

def setup(bot):
    bot.add_cog(SurveysReact(bot))
