from discord.ext import commands
from __main__ import send_cmd_help
from .utils import checks
from .utils.dataIO import dataIO
from .utils.chat_formatting import pagify, box
import discord, requests, random, os
try:
    from bs4 import BeautifulSoup
    soupAvailable = True
except:
    soupAvailable = False

DEFAULT_SETTINGS = {"send_in_channel" : False}

class Lyrics:

    def __init__(self, bot):
        self.bot = bot
        self.JSON = "data/Sitryk-Cogs/lyrics/settings.json"
        self.settings = dataIO.load_json(self.JSON)

    @commands.command(pass_context=True)
    async def lyrics(self, ctx, *, searchterm: str):
        """Used to fetch lyrics from a song
           Usage: [p]lyrics humble"""

        searchList = lyricsearch(searchterm)
        searchText = ""
        for index, item in enumerate(searchList):
            searchText += "\n\n**{}.** {}".format(index +1, " - ".join(item))
        chooseList = discord.Embed(description = searchText, color = discord.Color.red())
        chooseList.set_footer(text="*Type the corresponding number or 0 to cancel*")
        _sent_in = await self.bot.say(embed=chooseList)
        choice = await self.bot.wait_for_message(timeout=20, author = ctx.message.author, channel = ctx.message.channel)
        if choice is None:
            await self.bot.say("Cancelling lyric search.")
            return
        if not choice.content.isdigit():
            await self.bot.say("Cancelling lyric search.")
            return
        if int(choice.content) not in range(0, 11):
            await self.bot.say("Cancelling lyric search.")
            return
        if int(choice.content) == 0:
            await self.bot.say("Cancelling lyric search.")
            return
        else:
            if self.settings["send_in_channel"]:
                send = self.bot.say
            else:
                send = self.bot.whisper
            try:
                lyrics = pagify(lyricsearch(searchterm, int(choice.content)-1))
                await send("Here are the lyrics for **{}**\n\n".format(" - ".join(searchList[int(choice.content)-1])))
                for page in lyrics:
                    await send(page)
            except discord.DiscordException:
                await self.bot.say("I can't send messages to this user.")
            try:
                if self.settings["send_in_channel"]:
                    await self.bot.say("Here are the lyrics for **{}**".format(" - ".join(searchList[int(choice.content)-1])))
                else:
                    await self.bot.say("I've sent you the lyrics for **{}**".format(" - ".join(searchList[int(choice.content)-1])))
            except IndexError:
                await self.bot.say("Cancelling lyric search.")
                return
        
    @commands.group(name="lyricset", pass_context=True)
    async def _lyricset(self, ctx):
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            await self.bot.say(box("SEND IN CHANNEL: {}" .format(self.settings["send_in_channel"])))

    @_lyricset.command(name="channel", pass_context=True)
    @checks.mod()
    async def _lyricset_channel(self, ctx):
        """Toggle between sending in chat and sending to DMs"""
        self.settings["send_in_channel"] = not self.settings["send_in_channel"]
        dataIO.save_json(self.JSON, self.settings)
        if self.settings["send_in_channel"] == True:
            await self.bot.say("I will now send lyrics in the channel.")
        elif self.settings["send_in_channel"] == False:
            await self.bot.say("I will now send lyrics via message.")
        else:
            await self.bot.say("Huh, strange - try again maybe? ")

base_url = "https://api.genius.com"
headers = {'Authorization': 'Bearer 2wjXkB5_rWzVnEFOKwFMWhJOwvNPAlFDTywyaRK0jc3gtrCZjx8CsaXjzcE-2_4j'}  # Bearer Token should look like "Bearer" + token e.g. "Bearer 1234tokentokentoken"

def lyrics_from_song_api_path(song_api_path):
    song_url = base_url + song_api_path
    response = requests.get(song_url, headers=headers)
    json = response.json()
    path = json["response"]["song"]["path"]
    # gotta go regular html scraping... come on Genius
    page_url = "http://genius.com" + path
    page = requests.get(page_url)
    html = BeautifulSoup(page.text, "html.parser")
    # remove script tags that they put in the middle of the lyrics
    [h.extract() for h in html('script')]
    # at least Genius is nice and has a tag called 'lyrics'!
    lyrics = html.find("div", class_="lyrics").get_text()  # updated css where the lyrics are based in HTML
    return lyrics

def lyricsearch(searchterm, choice=None):
    search_url = base_url + "/search"
    data = {'q': searchterm}
    response = requests.get(search_url, data=data, headers=headers)
    json = response.json()
    song_info = None
    items = []

    for hit in json["response"]["hits"]:
        items.append([hit["result"]["primary_artist"]["name"], hit["result"]["title"]])

    if choice is None:
        return items
    else:
        song_info = json['response']['hits'][choice]['result']['api_path']
        return lyrics_from_song_api_path(song_info)

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
        dataIO.save_json(f, DEFAULT_SETTINGS)

def setup(bot):
    if soupAvailable:
        check_folders()
        check_files()
        n = Lyrics(bot)
        bot.add_cog(n)
    else:
        raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
