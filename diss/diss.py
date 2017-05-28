from __main__ import send_cmd_help
from discord.ext import commands
from random import choice
import discord

class Diss:
    """Example cog for dissing or respecting a user"""

    def __init__(self, bot):
        self.bot = bot
        self.users = { 'name1' : ['disses', 'disses2'], 'name2' : ['more disses', 'another diss']}

    @commands.command(name="diss", no_pm=True)
    async def _diss(self, name):
        userInDict = False
        if name in self.users:
            userInDict = True
        else:
            userInDict = False
        if userInDict is True:
            await self.bot.say(choice(self.users[name]))
        else:
            await self.bot.say("User is not listed.")

def setup(bot):
    n = Diss(bot)
    bot.add_cog(n)
