from discord.ext import commands

"""
Features regarding code interpretation and execution
"""

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