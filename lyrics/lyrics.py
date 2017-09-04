from discord.ext import commands
from __main__ import send_cmd_help
from .utils import checks
from .utils.dataIO import dataIO
from .utils.chat_formatting import pagify, box
import discord
import requests
import random
import os
import asyncio

try:
    from bs4 import BeautifulSoup
    soupAvailable = True
except:
    soupAvailable = False

DEFAULT_SETTINGS = {"CHANNEL": None}


class Lyrics:

    def __init__(self, bot):
        self.bot = bot
        self.JSON = "data/Sitryk-Cogs/lyrics/settings.json"
        self.settings = dataIO.load_json(self.JSON)

    @commands.command(pass_context=True)
    async def lyrics(self, ctx, *, query: str):
        """Used to fetch lyrics from a search query
           Usage: [p]lyrics white ferrari
                  [p]lyrics syrup sandwiches
           """

        server = ctx.message.server
        author = ctx.message.author

        place_holder = await self.bot.say(embed=discord.Embed(description="Gathering information...", colour=discord.Colour.orange()))

        items = lyricsearch(query)

        msg = "***Results based on a search for:***   *{}*".format(query)
        for item in items:
            msg += "\n\n**{}.** {} - {}".format(item, items[item]['song_title'], items[item]['artist_name'])

        choices = discord.Embed(description = msg, color = discord.Color.green())
        choices.set_footer(text="Type the corresponding number or 0 to cancel*")

        try:
            await self.bot.edit_message(place_holder, embed=choices)
        except:
            await self.bot.say("I need the \"Embed links\" Permission")
            return

        choice = await self.bot.wait_for_message(timeout=20, author = ctx.message.author, channel = place_holder.channel)

        if choice is None:
            await self.bot.edit_message(place_holder, embed=discord.Embed(description="Cancelling - Timed out", colour=discord.Colour.red()))
            return

        if not choice.content.isdigit():
            await self.bot.edit_message(place_holder, embed=discord.Embed(description="Cancelling - Invalid choice", colour=discord.Colour.red()))
            return

        if int(choice.content) not in range(0, len(items)+1):
            await self.bot.edit_message(place_holder, embed=discord.Embed(description="Cancelling - Choice not in list", colour=discord.Colour.red()))
            return

        if int(choice.content) == 0:
            await self.bot.edit_message(place_holder, embed=discord.Embed(description="Cancelling.", colour=discord.Colour.red()))
            return

        else:
            song = items[choice]['song_path']
            lyrics = lyrics_from_song_path(song)
            lyrics = pagify(lyrics)

            choice = int(choice.content)
            if self.settings[server.id]["CHANNEL"] is None:
                send = self.bot.whisper
                w = True
            else:
                w = False
                send = self.bot.send_message
                channel = discord.utils.find(lambda c: c.id == self.settings[server.id]["CHANNEL"], ctx.message.server.channels)

            if w is True:
                await self.bot.edit_message(place_holder, embed=discord.Embed(description="**I've sent you the lyrics for** ***{} - {}***\n\n".format(items[choice]['song_title'], items[choice]['artist_name']), color=discord.Color.green()))
                await send(embed=discord.Embed(description="**Following are the lyrics for** ***{} - {}***\n\n".format(items[choice]['song_title'], items[choice]['artist_name']), color=discord.Color.green()))
                asyncio.sleep(0.2)
                for page in lyrics:
                    asyncio.sleep(0.1)
                    await send(page)
            else:
                await send(channel, embed=discord.Embed(description="**Following are the lyrics for** ***{} - {}***\n\n".format(items[choice]['song_title'], items[choice]['artist_name']), color=discord.Color.green()))
                asyncio.sleep(0.2)
                for page in lyrics:
                    asyncio.sleep(0.1)
                    await send(channel, page)

    @commands.group(name="lyricset", pass_context=True)
    @checks.mod()
    async def _lyricset(self, ctx):
        """Used to change lyric settings"""
        server = ctx.message.server
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            channel = discord.utils.find(lambda c: c.id == self.settings[server.id]["CHANNEL"], ctx.message.server.channels)
            await self.bot.say("```\nLYRIC CHANNEL:\t{}\n```".format(ch))

    @_lyricset.command(name="channel", pass_context=True)
    async def _lyricset_channel(self, ctx, channel):
        """Set the channel in which lyrics are posted
        Whispers if no channel is set
        to remove channel just enter 'None'
        """

        server = ctx.message.server
        if channel is None:
            await send_cmd_help(ctx)
            return
        if channel is discord.Channel:
            self.settings[server.id]["CHANNEL"] = channel.id
            dataIO.save_json(self.JSON, self.settings)
            channel = discord.utils.find(lambda c: c.id == self.settings[server.id]["CHANNEL"], ctx.message.server.channels)
            await self.bot.say("Lyrics will now be sent to {}".format(channel.mention))
        elif channel == 'None':
            self.settings[server.id]["CHANNEL"] = None
            dataIO.save_json(self.JSON, self.settings)
            await self.bot.say("Lyrics will now be sent in DMs")
        else:
            await send_cmd_help(ctx)
            return


api_url = "https://api.genius.com"
headers = {'Authorization': 'Bearer 2wjXkB5_rWzVnEFOKwFMWhJOwvNPAlFDTywyaRK0jc3gtrCZjx8CsaXjzcE-2_4j'}  # Bearer Token should look like "Bearer" + token e.g. "Bearer 1234tokentokentoken"

def lyrics_from_song_path(song_api_path):
    song_url = api_url + song_api_path
    json = None

    with requests.get(song_url, headers=headers) as response:
        json = response.json()

    path = json["response"]["song"]["path"]
    page_url = "http://genius.com" + path
    page = requests.get(page_url)
    html = BeautifulSoup(page.text, "html.parser")
    [h.extract() for h in html('script')]

    lyrics = html.find("div", class_="lyrics").get_text()
    return lyrics

def lyricsearch(query:str):
    search_url = api_url + "/search"
    data = {'q': query}
    json = None
    try:
        with requests.get(search_url, data=data, headers=headers) as response:
            json = response.json()
    except:
        return None
    items = {}
    for index, hit in enumerate(json["response"]["hits"]):
        item = { index + 1 : {'song_title' : hit['result']['title'],
                              'artist_name' : hit['result']['primary_artist']['name'],
                              'song_path' : hit['result']['api_path']
                              }
                 }
        items.update(item)
    return items

def check_folders():
    paths = ["data/Sitryk-Cogs/lyrics"]
    for path in paths:
        if not os.path.exists(path):
            print("Creating {} folder...".format(path))
            os.makedirs(path)

def check_files():
    f = "data/Sitryk-Cogs/lyrics/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating empty settings.json...")
        dataIO.save_json(f, {})

def setup(bot):
    if soupAvailable:
        check_folders()
        check_files()
        n = Lyrics(bot)
        bot.add_cog(n)
    else:
        raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
