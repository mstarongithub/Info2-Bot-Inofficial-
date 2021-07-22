from discord.ext import commands

"""
Features regarding code interpretation and execution
"""

class SyntaxCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    