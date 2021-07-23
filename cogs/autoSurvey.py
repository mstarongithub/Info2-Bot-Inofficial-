"""
Command generated surveys
"""

import discord
from discord import message
from discord.ext import commands
from datetime import datetime
import dateparser

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
        Create a Survey Embed
        """

        body = f"*{desc}*\n"

        for o in range(len(options)):
            body += f'\n{self.__get_react(o)}:  **{options[o][0]}** *({options[o][1]} Votes)*'

        body += f'\n\n**Vote until {untl}**'

        embed = discord.Embed(
            title=name,
            color=0x6ffbaa
        )

        embed.add_field(name='Description: ', value=body)
        return embed
    
    @commands.has_permissions(manage_channels=True)
    @commands.command(
        description="*survey* \"name\" \"description\" \"until\" \"opt1\" ...")
    async def survey(self, context, *args):
        if len(args) >= 3:
            name = args[0]
            desc = args[1]
            untl = args[2]
            untl = dateparser.parse(untl).strftime("%m/%d/%Y, %H:%M:%S")
            opts = args[3:] if len(args) > 3 else ["Ja", "Nein"]
            opts = [[opts[i], 0] for i in range(len(opts))]

            message = await context.send(
                embed=self.__make_embed(name, desc, untl, opts)
            )

            path = f"surveys.{message.id}"

            self.bot.bot_data[f'{path}.name']        = name
            self.bot.bot_data[f'{path}.description'] = desc
            self.bot.bot_data[f'{path}.until']       = untl
            self.bot.bot_data[f'{path}.options']     = {
                self.__get_react(i): opts[i] for i in range(len(opts))
            }

            print(f'Survey created: {self.bot.bot_data[path]}')

            for o in range(len(opts)):
                await message.add_reaction(self.__get_react(i=o))
            
    async def update(self, ids):
        path = f"surveys.{ids[2]}"
        name = self.bot.bot_data[f'{path}.name']
        desc = self.bot.bot_data[f'{path}.description']
        untl = self.bot.bot_data[f'{path}.until']
        opts_raw = self.bot.bot_data[f'{path}.options']
        opts = [opts_raw[key] for key in opts_raw]

        assert len(ids) == 3

        channel = await self.bot.fetch_channel(ids[1])

        message = await channel.fetch_message(ids[2])

        await message.edit(
            embed=self.__make_embed(name, desc, untl, opts)
        )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        counter, ids = self.parse_reaction_payload(payload)
        if counter != None:
            self.bot.bot_data[counter] += 1
            print(f'Set {counter[:-4]} to {self.bot.bot_data[counter]}')
            await self.update(ids)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        counter, ids = self.parse_reaction_payload(payload)
        if counter != None:
            self.bot.bot_data[counter] -= 1
            print(f'Set {counter[:-4]} to {self.bot.bot_data[counter]}')
            await self.update(ids)

    def parse_reaction_payload(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id is None:
            return None, (None, None, None)  # Reaction is on a private message
        if payload.user_id == self.bot.user.id:
            return None, (None, None, None)  # Reaction is on a private message
        if f'surveys.{payload.message_id}' in self.bot.bot_data:
            path  = f"surveys.{payload.message_id}"
            if dateparser.parse(self.bot.bot_data[f'{path}.until']) > datetime.now():
                emoji = str(payload.emoji)
                if emoji in self.bot.bot_data[f'{path}.options']:
                    return f'{path}.options.{emoji}[1]', (
                        payload.guild_id,
                        payload.channel_id,
                        payload.message_id
                    )
        return None, (None, None, None)

def setup(bot):
    bot.add_cog(SurveysReact(bot))
