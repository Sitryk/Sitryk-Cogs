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

    def valid_choice(self, msg):
      if msg.content.isdigit() and eval(msg.content) in range(0, 11):
        return True
      return False

    @commands.command(pass_context=True)
    async def lyrics(self, ctx, *, searchterm: str):
        """Used to fetch lyrics from a song
            Usage: [p]lyrics humble"""

        searchList = lyricsearch(searchterm)
        searchText = ""
        for index, item in enumerate(searchList):
          searchText += "\n\n**{}.** {}".format(index +1, " - ".join(item)) 
        chooseList = discord.Embed(description = searchText,color=discord.Color.red())
        chooseList.set_footer(text="*Type the corresponding number or 0 to cancel*")
        _sent_in = await self.bot.say(embed=chooseList)
        choice = await self.bot.wait_for_message(timeout=180, author=ctx.message.author, channel=ctx.message.channel, check=self.valid_choice)
        if int(choice.content) == 0:
          await self.bot.say("Cancelling lyric search")
          return
        else:
          await self.bot.say("I've sent you the lyrics for **{}**".format(" - ".join(searchList[int(choice.content)-1])))
          try:
            lyrics = pagify(lyricsearch(searchterm, int(choice.content)-1))
            for page in lyrics:
              await self.bot.whisper(page)
          except discord.DiscordException:
            await self.bot.say("I can't send messages to this user.")
        

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

def setup(bot):
    if soupAvailable:
        n = LyricsCog(bot)
        bot.add_cog(n)
    else:
        raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
