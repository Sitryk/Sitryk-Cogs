from discord.ext import commands
from __main__ import send_cmd_help
import random, os, discord
from .utils import checks
from .utils.dataIO import dataIO

default_settings = {"default_colour" : "red"}

def returnhex():
    return random.randint(0, 0xFFFFFF)

def validhex(value):
    if value in range(0, 0x1000000):
        return True
    return False

class QuickEmbed:

    def __init__(self, bot):
        self.bot = bot
        self.JSON = "data/Sitryk-Cogs/quickembed/settings.json"
        self.data = dataIO.load_json(self.JSON)
        self.colours = { "red" : discord.Color.red,
                         "dark_red" : discord.Color.dark_red,
                         "blue" : discord.Color.blue,
                         "dark_blue" : discord.Color.dark_blue,
                         "teal" : discord.Color.teal,
                         "dark_teal" :discord.Color.dark_teal,
                         "green" : discord.Color.green,
                         "dark_green" : discord.Color.dark_green,
                         "purple" : discord.Color.purple,
                         "dark_purple" :discord.Color.dark_purple,
                         "magenta" : discord.Color.magenta,
                         "dark_magenta" : discord.Color.dark_magenta,
                         "gold" :discord.Color.gold,
                         "dark_gold" : discord.Color.dark_gold,
                         "orange" :discord.Color.orange,
                         "dark_orange" :discord.Color.dark_orange,
                         "random" : returnhex
                         }


    @commands.group(name="qeset", pass_context=True)
    @checks.is_owner()
    async def _qeset(self, ctx):
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            await self.bot.say("```\nDEFAULT COLOUR: {}\n```".format(self.data["default_colour"]))

    @_qeset.command(aliases=[color], name="colour")
    async def _qeset_defaultcolour(self, colour):
        """Used to change the default colour of embeds if a colour is not specified"""
        if colour.lower() not in self.colours:
            await self.bot.say("Sorry! Trouble setting {} as your default colour.".format(colour))
            return
        else:
            self.data["default_colour"] = colour.lower()
            dataIO.save_json(self.JSON, self.data)
        await self.bot.say("Default embed colour changed to: " + colour) 

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def qembed(self, ctx, text, color=None):
        """Used to make a quick embed
        
        {server} is ctx.message.server
        {author} is ctx.message.author
        {channel} is ctx.message.channel
        {message} is ctx.message
        {ctx} is ctx
        """

        if color is None:
            embed_color = self.colours[self.data["default_colour"]]()
        elif color.lower() not in self.colours:
            if color.startswith('#'):
                color = color[1:]
            try:
                if validhex(int(color, 16)):
                    embed_color = discord.Color(int(color, 16))
            except ValueError:
                await self.bot.send_cmd_help(ctx)
                return
            if not validhex(int(color, 16)):
                await self.bot.send_cmd_help(ctx)
                return
        else:
            embed_color = self.colours[color]()
        
        embed = discord.Embed(description=text.format(server=ctx.message.server, author=ctx.message.author, channel=ctx.message.channel, message=ctx.message, ctx=ctx), color=embed_color)
        await self.bot.say(embed=embed)

def check_folders():
    paths = ["data/Sitryk-Cogs/quickembed"]
    for path in paths:
        if not os.path.exists(path):
            print("Creating {} folder...".format(path))
            os.makedirs(path)


def check_files():
    serverSettings = {"default_colour" : "red"}

    f = "data/Sitryk-Cogs/quickembed/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating empty quickembed's settings.json...")
        dataIO.save_json(f, serverSettings)

def setup(bot):
    check_folders()
    check_files()
    n = QuickEmbed(bot)
    bot.add_cog(n)
