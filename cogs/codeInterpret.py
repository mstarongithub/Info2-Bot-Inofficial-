"""
Features regarding code interpretation and execution
"""

from discord.ext import commands

from pistonapi import PistonAPI

class SyntaxCheck(commands.Cog):
    """
    Check the syntax of code blocks
    """

    def __init__(self, bot):
        self.bot = bot

class ExecCode(commands.Cog):
    """
    Execute code and display it´s output
    """

    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(SyntaxCheck(bot))
    bot.add_cog(ExecCode(bot))