from discord.ext import commands
from .utils.chat_formatting import pagify
import discord, requests, random
try:
  from bs4 import BeautifulSoup
  soupAvailable = True
except:
  soupAvailable = False

class LyricsCog:

    def __init__(self, bot):
        self.bot = bot
        self.song = ""
        self.artist = ""

    @commands.command(pass_context=True)
    async def lyrics(self, ctx, searchterm):
        """Used to fetch lyrics from a song

            Usage: [p]lyric 'kendrick lamar' 'humble' """

        if artist == "":
            await self.bot.say("Please supply an artist")
        elif song == "":
            await self.bot.say("Please supply a song title")
        else:
            searchList = lyricsearch(searchterm)
            searchText
            for index, item in enumerate(searchList):
              searchText += "\n\n**{}.** {} - {}".format(index +1, searchList[0], searchList[1]) 
            chooseList = discord.Embed(description = searchText,color=discord.Color(random.randint(0, 0xffffff)))
            await self.bot.say(embed = chooseList)
            #lyrics = lyricsearch(searchterm)
            #if lyrics == None:
                #await self.bot.whisper("Sorry! I couldn't find any lyrics with your search terms.")
            #else:
                #try:
                    #lyrics = pagify(lyrics)
                    #for page in lyrics:
                        #await self.bot.whisper(page)
                #except discord.DiscordException:
                    #await self.bot.say("I can't send messages to this user.")
        

base_url = "https://api.genius.com"
headers = {'Authorization': 'Bearer 2wjXkB5_rWzVnEFOKwFMWhJOwvNPAlFDTywyaRK0jc3gtrCZjx8CsaXjzcE-2_4j'} # Bearer Token should look like "Bearer" + token e.g. "Bearer 1234tokentokentoken"

def lyrics_from_song_api_path(song_api_path):
  song_url = base_url + song_api_path
  response = requests.get(song_url, headers=headers)
  json = response.json()
  path = json["response"]["song"]["path"]
  #gotta go regular html scraping... come on Genius
  page_url = "http://genius.com" + path
  page = requests.get(page_url)
  html = BeautifulSoup(page.text, "html.parser")
  #remove script tags that they put in the middle of the lyrics
  [h.extract() for h in html('script')]
  #at least Genius is nice and has a tag called 'lyrics'!
  lyrics = html.find("div", class_="lyrics").get_text() #updated css where the lyrics are based in HTML
  return lyrics

def lyricsearch(searchterm):
  search_url = base_url + "/search"
  data = {'q': searchterm}
  response = requests.get(search_url, data=data, headers=headers)
  json = response.json()
  song_info = None
  items = []
  for hit in json["response"]["hits"]:
    items.append([hit["result"]["primary_artist"]["name"], hit["result"]["title"]])
  return items
    #if hit["result"]["primary_artist"]["name"].lower() == artist.lower():
    #  song_info = hit
    #  break
  #if song_info:
  #  song_api_path = song_info["result"]["api_path"]
  #  return lyrics_from_song_api_path(song_api_path)

def setup(bot):
    if soupAvailable:
        n = LyricsCog(bot)
        bot.add_cog(n)
    else:
        raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
