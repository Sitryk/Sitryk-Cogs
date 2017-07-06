from discord.ext import commands
from __main__ import send_cmd_help
import random, os, discord
from .utils.dataIO import dataIO

default_settings = {"default_colour" : "red"}
def returnhex():
    return random.randint(0, 0xFFFFFF)
class QEmbed:

    def __init__(self, bot):
        self.bot = bot
        self.JSON = "data/Sitryk-Cogs/quickembed/settings.json"
        self.data = dataIO.load_json(self.JSON)
        self.colours = { "red" : discord.Color.red,
                         "dark_red" : discord.Color.dark_red,
                         "blue" : discord.Color.blue(),
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
    async def _qeset(self, ctx):
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @_qeset.command(name="defaultColour")
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
    async def qembed(self, ctx, text, color=None):
        """Used to make a quick embed
        
        {0} corresponds to server, a hexadecimal code can be used without a hashtag"""
        if color is None:
            embed_color = self.colours[self.data["default_colour"]]()
        elif color.lower() not in self.colours:
            if len(color) == 6:
                try:
                    color = int(color, 16)
                    embed_color = discord.Color(color)
                except:
                    embed_color = self.colours[self.data["default_colour"]]()
            else:
                msg = "Available colors: \n"
                for x in self.colours:
                    msg += "\n" + x
                msg += "\n\nNote: You can also use hex color codes e.g. " + ctx.prefix + "qembed test ff0000"
                await self.bot.whisper("```fix\n" + msg + "\n```")
                return
        else:
            embed_color = self.colours[color]()
        embed = discord.Embed(description=text.format(ctx.message.server), color=embed_color)
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
    n = QEmbed(bot)
    bot.add_cog(n)
