from discord.ext import commands
import redbot.core
from redbot.core.utils import chat_formatting as cf
from redbot.core.data_manager import storage_type
from redbot.core.events import _get_startup_screen_specs

import os
import discord
import pkg_resources
from colorama import Fore, Style, init
from pkg_resources import DistributionNotFound


INTRO = """
______         _           ______ _                       _  ______       _   
| ___ \       | |          |  _  (_)                     | | | ___ \     | |  
| |_/ /___  __| |  ______  | | | |_ ___  ___ ___  _ __ __| | | |_/ / ___ | |_ 
|    // _ \/ _` | |______| | | | | / __|/ __/ _ \| '__/ _` | | ___ \/ _ \| __|
| |\ \  __/ (_| |          | |/ /| \__ \ (_| (_) | | | (_| | | |_/ / (_) | |_ 
\_| \_\___|\__,_|          |___/ |_|___/\___\___/|_|  \__,_| \____/ \___/ \__|
"""


class ClearConsole:

    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(hidden=True, aliases=['clc', 'cls', 'clearconsole'])
    async def cleanconsole(self, ctx):
        """
        Clear the console of errors
        """
        os.system('cls')

        guilds = len(self.bot.guilds)
        users = len(set([m for m in self.bot.get_all_members()]))

        try:
            data = await self.bot.application_info()
            invite_url = discord.utils.oauth_url(data.id)
        except:
            if bot.user.bot:
                invite_url = "Could not fetch invite url"
            else:
                invite_url = None

        prefixes = await self.bot.db.prefix()
        lang = await self.bot.db.locale()
        red_version = redbot.core.__version__
        red_pkg = pkg_resources.get_distribution("Red-DiscordBot")
        dpy_version = discord.__version__

        INFO = [str(self.bot.user), "Prefixes: {}".format(', '.join(prefixes)),
                'Language: {}'.format(lang),
                "Red Bot Version: {}".format(red_version),
                "Discord.py Version: {}".format(dpy_version),
                "Shards: {}".format(self.bot.shard_count)]

        if guilds:
            INFO.extend(("Guilds: {}".format(guilds), "Users: {}".format(users)))
        else:
            print("Ready. I'm not in any guild yet!")

        INFO.append('{} cogs with {} commands'.format(len(self.bot.cogs), len(self.bot.commands)))

        INFO2 = []

        sentry = await self.bot.db.enable_sentry()
        mongo_enabled = storage_type() != "JSON"
        reqs_installed = {
            "voice": None,
            "docs": None,
            "test": None
        }
        for key in reqs_installed.keys():
            reqs = [x.name for x in red_pkg._dep_map[key]]
            try:
                pkg_resources.require(reqs)
            except DistributionNotFound:
                reqs_installed[key] = False
            else:
                reqs_installed[key] = True

        options = (
            ("Error Reporting", sentry),
            ("MongoDB", mongo_enabled),
            ("Voice", reqs_installed["voice"]),
            ("Docs", reqs_installed["docs"]),
            ("Tests", reqs_installed["test"])
        )

        on_symbol, off_symbol, ascii_border = _get_startup_screen_specs()

        for option, enabled in options:
            enabled = on_symbol if enabled else off_symbol
            INFO2.append("{} {}".format(enabled, option))

        print(Fore.RED + INTRO)
        print(Style.RESET_ALL)
        print(cf.bordered(INFO, INFO2, ascii_border=ascii_border))

        if invite_url:
            print("\nInvite URL: {}\n".format(invite_url))

        await ctx.send('Console Reset')
