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
    """
    Simple reaction surveys with time limit
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} ready")

    __numbers = [
        "{}\N{COMBINING ENCLOSING KEYCAP}".format(num) for num in range(1, 10)
    ]

    def __get_react(self, i=0):
        """
        Return reaction for Index
        """

        assert i < 9

        return f'{self.__numbers[i]}'

    def __make_embed(self, name, desc, untl, options, done=False):
        """
        Create a Survey Embed
        """

        body = f"*{desc}*\n"

        for o in range(len(options)):
            if done:
                body += f'\n**{options[o][0]}** got **{options[o][1]} Votes**'
            else:
                body += f'\n{self.__get_react(o)}:  **{options[o][0]}** *({options[o][1]} Votes)*'

        body += f'\n\n**Closed at {untl}**' if done else f'\n\n**Vote until {untl}**'

        embed = discord.Embed(
            title=name,
            color=0x6ffbaa
        )

        embed.add_field(name='Description: ', value=body)
        return embed

    
    def __get_path(self, survey_id):
        path = f'surveys.{survey_id}'

        if path not in self.bot.bot_data:
            return None

        return path

    def __get_attr(self, survey_id, attr):
        if self.__get_path(survey_id) == None:
            return None
        
        return self.bot.bot_data[f'{self.__get_path(survey_id)}.{attr}']

    def __set_attr(self, survey_id, attr, value):        
        self.bot.bot_data[f'surveys.{survey_id}.{attr}'] = value

    def __is_done(self, survey_id):
        if self.__get_path(survey_id) == None:
            return True

        return dateparser.parse(self.__get_attr(survey_id, 'until')) < datetime.now()

    def __parse_reaction_payload(self, payload: discord.RawReactionActionEvent):
        """
        Parse user reaction and check if message is a survey
        """

        if payload.guild_id is None:
            return None, None  # Reaction is on a private message
        
        if payload.user_id == self.bot.user.id:
            return None, None  # Dont count bot reactions
        
        if self.__get_path(payload.message_id) != None:
            if not self.__is_done(payload.message_id):
                emoji = str(payload.emoji)
                if emoji in self.__get_attr(payload.message_id, 'options'):
                    return f'{self.__get_path(payload.message_id)}.options.{emoji}[1]', payload.channel_id
        
        return None, payload.channel_id
    
    @commands.command(
        description="*survey* \"name\" \"description\" \"until\" \"opt1\" ...")
    async def survey(self, context, *args):
        """
        Create a new survey
        Format: `survey "name" "description" "until" "Option 1" "Option 2" ...`
        """

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

            self.__set_attr(message.id, 'name', name)
            self.__set_attr(message.id, 'description', desc)
            self.__set_attr(message.id, 'until', untl)
            self.__set_attr(
                message.id, 
                'options', 
                {self.__get_react(i): opts[i] for i in range(len(opts))}
            )

            print(f'Survey created: {message.id}')

            for o in range(len(opts)):
                await message.add_reaction(self.__get_react(i=o))
    
    async def update_all(self, channel_id):
        for message_id in self.bot.bot_data['surveys']:
            await self.update(message_id, channel_id)
        for message_id in list(self.bot.bot_data['surveys']):
            if self.__is_done(message_id):
                del self.bot.bot_data[self.__get_path(message_id)]

    async def update(self, message_id, channel_id):
        """
        Update a survey message
        """

        if self.__get_path(message_id) == None:
            raise KeyError(f'\"{message_id}\" is not a survey')

        print(f'Updated Survey: {message_id}')

        name = self.__get_attr(message_id, 'name')
        desc = self.__get_attr(message_id, 'description')
        untl = self.__get_attr(message_id, 'until')
        opts_raw = self.__get_attr(message_id, 'options')
        opts = [opts_raw[key] for key in opts_raw]

        channel = await self.bot.fetch_channel(channel_id)

        message = await channel.fetch_message(message_id)

        await message.edit(
            embed=self.__make_embed(
                name, 
                desc, 
                untl, 
                opts, 
                done=self.__is_done(message_id)
            )
        )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """
        Increment when reaction is clicked by user
        """

        counter, channel = self.__parse_reaction_payload(payload)
        if counter != None:
            self.bot.bot_data[counter] += 1
            print(f'Set {counter[:-4]} to {self.bot.bot_data[counter]} (++)')
        await self.update_all(channel)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """
        Decrement when reaction is unclicked by user
        """

        counter, channel = self.__parse_reaction_payload(payload)
        if counter != None:
            self.bot.bot_data[counter] -= 1
            print(f'Set {counter[:-4]} to {self.bot.bot_data[counter]} (--)')
        if channel != None:
            await self.update_all(channel)

def setup(bot):
    bot.add_cog(SurveysReact(bot))
