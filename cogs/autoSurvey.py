"""
Command generated surveys
"""

import discord
from discord import RawReactionActionEvent, Embed
from discord.ext import commands
from datetime import datetime
import dateparser
from typing import Union

__authors__ = "Frederik Beimgraben"
__credits__ = ["Frederik Beimgraben"]
__maintainer__ = "Frederik Beimgraben"
__email__ = "beimgraben8@gmail.com"
__status__ = "WIP"


class SurveysReact(commands.Cog):
    """Simple reaction surveys with time limit"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Print class name to stdout once ready"""

        print(f"{self.__class__.__name__} ready")

    # Number Keycap Emojis
    __numbers = [
        "{}\N{COMBINING ENCLOSING KEYCAP}".format(num) for num in range(1, 10)
    ]

    def __get_survey_react(self, i: int = 0) -> str:
        """Return reaction for Index"""

        assert i < 9

        return f'{self.__numbers[i]}'

    def __make_embed(self, name: str, desc: str,
                     untl: str, options: list, done: bool = False) -> Embed:
        """Create a Survey Embed"""

        body = f"*{desc}*\n"

        for o in range(len(options)):
            if done:
                body += f'\n**{options[o][0]}** got **{options[o][1]} Votes**'
            else:
                body += f'\n{self.__get_survey_react(o)}:  '
                body += f'**{options[o][0]}** *({options[o][1]} Votes)*'

        body += (
            f'\n\n**Closed at {untl}**' if done
            else f'\n\n**Vote until {untl}**'
        )

        embed = discord.Embed(
            title=name,
            color=0x6ffbaa
        )

        embed.add_field(name='Description: ', value=body)
        return embed

    def __get_survey_path(self, survey_id: Union[str, int],
                          must_exist: bool = True) -> str:
        """Get path to a survey in `bot_data`. `None` if not in `bot_data`"""

        path = f'surveys.{survey_id}'

        if path not in self.bot.bot_data and must_exist:
            return None

        return path

    def __get_survey_attr(self, survey_id: Union[str, int], attr: str):
        """Get a attribute (subpath) for a survey"""

        if self.__get_survey_path(survey_id) is None:
            return None

        attr_path = f'{self.__get_survey_path(survey_id)}.{attr}'

        return self.bot.bot_data[attr_path]

    def __set_survey_attr(self, survey_id: Union[str, int], attr: str,
                          value):
        """Set a attribute (subpath) for a survey"""

        attr_path = f'{self.__get_survey_path(survey_id, False)}.{attr}'

        self.bot.bot_data[attr_path] = value

    def __until(self, survey_id: Union[str, int]) -> datetime:
        if self.__get_survey_path(survey_id) is None:
            return datetime.now()

        return dateparser.parse(self.__get_survey_attr(survey_id, 'until'))

    def __is_done(self, survey_id: Union[str, int]) -> bool:
        """Has the participation period already ended?"""

        if self.__get_survey_path(survey_id) is None:
            return False

        return self.__until(survey_id) < datetime.now()

    def __parse_reaction_payload(self, payload: RawReactionActionEvent):
        """Parse user reaction and check if message is a survey"""

        if payload.guild_id is None:
            return None, None, None  # Reaction is on a private message

        if payload.user_id == self.bot.user.id:
            return None, None, None  # Dont count bot reactions

        if self.__get_survey_path(payload.message_id) is not None:
            if not self.__is_done(payload.message_id):
                emoji = str(payload.emoji)
                options = self.__get_survey_attr(payload.message_id, 'options')
                if emoji in options:
                    return (
                        self.__get_survey_path(payload.message_id) +
                        f'.options.{emoji}[1]',
                        payload.channel_id,
                        payload.message_id
                    )

        return None, payload.channel_id, payload.message_id

    @commands.command(description="Create a new survey")
    async def survey(self, context, *args):
        """
        Create a new survey
        Format: `survey "name" "description" "until" "Option 1" "Option 2" ...`
        """

        if len(args) >= 3:
            name = args[0]
            desc = args[1]
            untl = args[2]
            time_parsed = dateparser.parse(untl)

            if time_parsed < datetime.now():
                return await context.send(
                    'Survey end can´t be in the past!'
                )
            elif time_parsed is None:
                return await context.send(
                    'Time format incorrect!'
                )
            else:
                untl = time_parsed.strftime("%m/%d/%Y, %H:%M:%S")

            opts = args[3:] if len(args) > 3 else ["Yes", "No"]
            opts = [[opts[i], 0] for i in range(len(opts))]

            message = await context.send(
                embed=self.__make_embed(name, desc, untl, opts)
            )

            self.__set_survey_attr(message.id, 'name', name)
            self.__set_survey_attr(message.id, 'description', desc)
            self.__set_survey_attr(message.id, 'until', untl)
            self.__set_survey_attr(
                message.id,
                'options',
                {self.__get_survey_react(i): opts[i] for i in range(len(opts))}
            )

            print(f'Survey created: {message.id}')

            for o in range(len(opts)):
                await message.add_reaction(self.__get_survey_react(i=o))

    async def update_all(self, channel_id: Union[str, int]):
        """Update all surveys in `channel_id`"""

        for message_id in list(self.bot.bot_data['surveys']):
            await self.update(message_id, channel_id)

    async def update(self, message_id: Union[str, int],
                     channel_id: Union[str, int]):
        """Update a survey message"""

        if channel_id is None or message_id is None:
            return

        if self.__get_survey_path(message_id) is None:
            raise KeyError(f'\"{message_id}\" is not a survey')

        try:
            channel = await self.bot.fetch_channel(channel_id)
        except discord.errors.NotFound:
            return

        try:
            message = await channel.fetch_message(message_id)
        except discord.errors.NotFound:
            return

        print(f'Updated Survey: {message_id}')

        name = self.__get_survey_attr(message_id, 'name')
        desc = self.__get_survey_attr(message_id, 'description')
        untl = self.__get_survey_attr(message_id, 'until')
        opts_raw = self.__get_survey_attr(message_id, 'options')
        opts = [opts_raw[key] for key in opts_raw]

        await message.edit(
            embed=self.__make_embed(
                name,
                desc,
                untl,
                opts,
                done=self.__is_done(message_id)
            )
        )

        if self.__is_done(message_id):
            del self.bot.bot_data[self.__get_survey_path(message_id)]

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        """Increment when reaction is clicked by user"""

        counter, channel, message = self.__parse_reaction_payload(payload)
        if counter is not None:
            self.bot.bot_data[counter] += 1
            print(f'Set {counter[:-4]} to {self.bot.bot_data[counter]} (++)')
            await self.update(message, channel)
        if self.__get_survey_path(message) is not None:
            await self.update(message, channel)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        """Decrement when reaction is unclicked by user"""

        counter, channel, message = self.__parse_reaction_payload(payload)
        if counter is not None:
            self.bot.bot_data[counter] -= 1
            print(f'Set {counter[:-4]} to {self.bot.bot_data[counter]} (--)')
            await self.update(message, channel)
        if self.__get_survey_path(message) is not None:
            await self.update(message, channel)


def setup(bot):
    bot.add_cog(SurveysReact(bot))
