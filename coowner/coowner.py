from .utils import chat_formatting as cf
from .utils.dataIO import dataIO
from discord.ext import commands
from .utils import checks
from copy import deepcopy
import discord
import random
import os

DEFAULT_SETTINGS = {"RESTRICTED": [],
                    "WHITELIST" : [],
                    "WL_ENABLED" : False,
                    "BLACKLIST" : [],
                    "BL_ENABLED" : False,
                    "USERS": {}
                    }


class CoOwner:
    """Allows you the ability to add co-owners that have access to owner privilege commands"""

    def __init__(self, bot):
        self.bot = bot
        self.path = "data/Sitryk-Cogs/coowner/settings.json"
        self.settings = dataIO.load_json(self.path)

    @commands.command(pass_context=True, no_pm=True)
    async def odus(self, ctx, *, command):
        """ Runs the [command] as if the owner had run it. DO NOT ADD A PREFIX
        """

        server = ctx.message.server
        author = ctx.message.author
        AliasCog = self.bot.get_cog('Alias')
        if AliasCog:
            alias_loaded = False
        else:
            alias_loaded = True
        if author.id not in self.settings["USERS"]:
            return


        t = True if self.bot.get_command(command) else False
        if not t and alias_loaded:
            t = True if command in AliasCog.aliases[server.id] else False
        if t:
            pass
        else:
            return

        allowed = True

        if self.settings["WL_ENABLED"]: # if whitelist enabled
            cmds = []
            for i in self.settings["WHITELIST"]:
                cmds += list(filter(lambda c: c.cog_name == i, self.bot.commands.values())) # list: all cmds for cogs in whitelist
            for cmd in cmds:
                if command.startswith(cmd.qualified_name): # if odus command startswith a whitelisted name, allow it.
                    allowed = True
                    break
                else:
                    allowed = False

        if self.settings["BL_ENABLED"]: # if blacklist enabled
            cmds = []
            for i in self.settings["BLACKLIST"]:
                cmds += list(filter(lambda c: c.cog_name == i, self.bot.commands.values())) # list: all parent cmds for cogs in blacklist
            for cmd in cmds:
                if command.startswith(cmd.qualified_name): # if odus commands starts with blacklisted name, deny it
                    allowed = False
                    break
                else:
                    allowed = True

        if len(self.settings["RESTRICTED"]) > 0: # if restrict list has items
            for cmd in self.settings["RESTRICTED"]:
                if command.startswith(cmd): # check if the odus command starts with a restricted command, deny it if so
                    allowed = False
                    break
                else:
                    allowed = True

        if len(self.settings["USERS"][author.id]["RESTRICTED"]) > 0 and allowed: # check if the user has any restricted commands
            for cmd in self.settings["USERS"][author.id]["RESTRICTED"]:
                if command.startswith(cmd): # check if the odus command starts with a restricted command, deny it if so
                    allowed = False
                    break
                else:
                    allowed = True

        if len(AliasCog.aliases[server.id]) > 0 and allowed and alias_loaded: # if there are aliases for this server and we are allowed through so far
            for alias in AliasCog.aliases[server.id]:
                if len(self.settings["RESTRICTED"]) > 0 and allowed:
                    for cmd2 in self.settings["RESTRICTED"]: 
                        if alias == cmd2 or AliasCog.aliases[server.id][alias].startswith(cmd2): # for each alias, if the alias has the same name as a restricted command, deny
                            allowed = False                                  # or if the alias' command starts with a restricted command, deny
                            break
                        else:
                            allowed = True
                if allowed == False:
                    break
                if len(self.settings["USERS"][author.id]["RESTRICTED"]) > 0 and allowed:
                    for cmd2 in self.settings["USERS"][author.id]["RESTRICTED"]:
                        if alias == cmd2 or AliasCog.aliases[server.id][alias].startswith(cmd2): # for each alias, if the alias has the same name as a users restricted command, deny
                            allowed = False                                  # or if the alias' command starts with a restricted command, deny
                            break
                        else:
                            allowed = True
                if allowed == False:
                    break

        if author.id in self.settings["USERS"] and allowed:
            new_message = deepcopy(ctx.message)
            new_message.author = discord.utils.get(self.bot.get_all_members(), id=self.bot.settings.owner)
            new_message.content = self.bot.settings.get_prefixes(new_message.server)[0] \
                + command
            await self.bot.process_commands(new_message)
        elif author.id in self.settings["USERS"]:
            if command in self.settings["RESTRICTED"] or (command in self.settings["BLACKLIST"] and self.settings["BL_ENABLED"]) or (command not in self.settings["WHITELIST"] and self.settings["WL_ENABLED"]):
                prefix = "Co-Owners"
            else:
                prefix = "You"
            await self.bot.say("{} are restricted from using this command".format(prefix))
            return
        else:
            await self.bot.say("You are not a co-owner")
            return

    @commands.group(name='co-owner', pass_context=True)
    @checks.is_owner()
    async def _co_owner(self, ctx):
        """Add or remove co-owners `[p]co-owner info` for more"""

        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)
            users = []
            for id in self.settings["USERS"]:
                try:
                    users.append(discord.utils.get(self.bot.get_all_members(), id=id))
                except:
                    pass
            msg = "Current co-owners:\n\n"
            if len(users) < 1:
                await self.bot.say("```fix\nYou have no co-owners\n```")
                return
            for co in users:
                name2 = ' / '+ co.display_name if co.display_name != co.name else ""
                msg += "[{0.name}{1}] - <{0.id}>\n".format(co, name2)
            await self.bot.say(cf.box(msg))
            return

    @_co_owner.command(pass_context=True, hidden=True)
    async def reset(self, ctx):
        """This will reset all co-owner settings to default"""
        await self.bot.say("Are you sure you want to reset all settings to default?")
        confirm = await self._confirm_owner(ctx)
        if not confirm:
            return
        self.settings = DEFAULT_SETTINGS
        dataIO.save_json(self.path, self.settings)
        await self.bot.say("Settings reset.")

    @_co_owner.command(pass_context=True, hidden=True)
    async def info(self, ctx, option):
        """How to use the co-owner cog
        
        options: odus, co-owner, restrict
        """
        server = ctx.message.server
        options = ['odus', 'co-owner', 'restrict']
        msgs = {'odus' :"**Odus**:\n"
                        "`[p]odus [command]` odus is the main command co-owners will use.\n\n"
                        "`[p]odus` will invoke the command as if the owner of the bot had invoked it themselves "
                        "so make sure to be careful and only add co-owners you can really trust.\n\n"

                        "**Side note**:\n"
                        "The command is named after Red-DiscordBot's v2 sudo which would allow you to imitate a different user. "
                        "Because this works backwards to allow a user to imitate the owner, I felt odus fit",
                'co-owner' :"**Co-Owner**:\n"
                            "`[p]co-owner` is the command which you will use to add, remove and show this text.\n\n"
                            "`[p]co-owner add [user]` will add the [user] as a co-owner, there will be confirmation messages to ensure intentions.\n\n"
                            "`[p]co-owner remove` will list out all current co-owners and ask you to choose one to remove.",
                'restrict' :"**Restrict**:\n"
                            "`[p]restrict` is your best shot at restricting what co-owners are able to use while still maintaining owner access\n\n"
                            "`[p]restrict addcommand [command]` will restrict the [command] for all co-owners so they cannot use it through odus \n— *Aliases: ['addcmd']*\n\n"
                            "`[p]restrict delcommand [command]` will remove the restriction on [command] for all co-owners so they can use it through odus \n— *Aliases: ['delcmd']*\n\n"
                            "`[p]restrict adduser [user] [command]` will restrict the co-owner [user] from being able to use the [command] in odus\n\n"
                            "`[p]restrict deluser [user] [command]` will remove the restriction of [command] for the [user]\n\n"
                            "`[p]restrict whitelist [cog]` will only allow commands from that cog to be used in odus - you can whitelist multiple cogs \n— *Aliases: ['wl']*\n\n"
                            "`[p]restrict delwhitelist [cog]` will allow you to remove a cog from the whitelist - enabling whitelist will disable blacklist \n— *Aliases: ['delwl']*\n\n"
                            "`[p]restrict blacklist [cog]` will allow you to blacklist commands from a cog so co-owners cannot use it in odus \n— *Aliases: ['bl']*\n\n"
                            "`[p]restrict delblacklist [cog]` will allow you to remove a cog from the blacklist - enabling blacklist will disable whitelist \n— *Aliases: ['delbl']*"
                }

        if option in options:
            em = discord.Embed(description=msgs[option], colour=discord.Colour.orange())
            em.set_thumbnail(url=server.icon_url)
            await self.bot.say(embed=em)
        else:
            await self.bot.say("That is not a listed option.")

    @_co_owner.command(pass_context=True)
    async def add(self, ctx, user: discord.User):
        """Add a co-owner by mentioning them"""

        self.bot.say("Are you sure you want to add **{}** as a co-owner?".format(user.display_name))
        confirm = await self._confirm_owner(ctx)
        if not confirm:
            return

        if user.id not in self.settings["USERS"]:
            self.settings["USERS"][user.id] = {"RESTRICTED" : []}
            dataIO.save_json(self.path, self.settings)
            await self.bot.say("**{0.display_name}** *<{0.id}>* has been added as a co-owner".format(user))
            return
        elif user.id in self.settings["USERS"]:
            await self.bot.say("That user is already a co-owner")
            return


    @_co_owner.command(pass_context=True)
    async def remove(self, ctx):
        """Remove a co-owner from a list of current co-owners"""

        owner = discord.utils.get(self.bot.get_all_members(), id=self.bot.settings.owner)
        co_owners = []
        for co_owner_id in self.settings["USERS"]:
            memberObj = discord.utils.get(self.bot.get_all_members(), id=co_owner_id)
            co_owners.append(memberObj)
        if len(co_owners) > 0:
            confirm = await self._confirm_owner(ctx)
            if not confirm:
                return
            msg = ""
            for index, co in enumerate(co_owners):
                msg += "{0}. {1.name} {1.id}\n".format(index + 1, co)
            await self.bot.say("```\n{}```".format(msg))
            await self.bot.say("\nChoose the corresponding number to remove the user or 0 to cancel")
            choice = await self.bot.wait_for_message(timeout=15, author=owner, channel=ctx.message.channel)
            
            if choice is None:
                await self.bot.say("Cancelled - Timed out")
                return
            if not choice.content.isdigit():
                await self.bot.say("Cancelled - Choice is NaN")
                return
            if int(choice.content) not in range(0, len(co_owners)+1):
                await self.bot.say("Cancelled - Choice is not in range")
                return
            if int(choice.content) == 0:
                await self.bot.say("Cancelled")
                return
            to_remove = co_owners[int(choice.content)-1]
            await self.bot.say("Removing: **{0.name} <{0.id}>** as a co-owner".format(to_remove))
            del(self.settings["USERS"][to_remove.id])
            dataIO.save_json(self.path, self.settings)
            await self.bot.say("Done.")
        else:
            await self.bot.say("```fix\nYou have no co-owners\n```")
            return


    @commands.group(pass_context=True)
    @checks.is_owner()
    async def restrict(self, ctx):
        """ Add/Remove Co-owner related restrictions"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)
            msg = ""
            if self.settings["RESTRICTED"]:
                msg += "Co-owner restricted commands:\n\n"
                msg += ", ".join(self.settings["RESTRICTED"])
            if self.settings["WL_ENABLED"]:
                msg += "\n\nWhitelisted cogs: \n\n"
                msg += ", ".join(self.settings["WHITELIST"])
            if self.settings["BL_ENABLED"]:
                msg += "\n\nBlacklisted cogs: \n\n"
                msg += ", ".join(self.settings["BLACKLIST"])
            if msg != "":
                await self.bot.say(cf.box(msg))
            return

    @restrict.command(aliases=['addcmd'], pass_context=True)
    async def addcommand(self, ctx, *, command):
        """Restricts all co-owners from using [command] """
        
        confirm = await self._confirm_owner(ctx)
        if not confirm:
            return

        AliasCog = self.bot.get_cog('Alias')
        if AliasCog:
            alias_loaded = False
        else:
            alias_loaded = True
        server = ctx.message.server
        t = True if self.bot.get_command(command) else False
        if not t and alias_loaded:
            t = True if command in AliasCog.aliases[server.id] else False
        if t and command not in self.settings["RESTRICTED"]:
            await self.bot.say("**All owners will be restricted from using**: {}".format(command))
            self.settings["RESTRICTED"].append(command)
            dataIO.save_json(self.path, self.settings)
        elif command in self.settings["RESTRICTED"]:
            await self.bot.say("{} is already a restricted command".format(command))
        else:
            await self.bot.say("{} is not a valid command.".format(command))

    @restrict.command(aliases=['delcmd'], pass_context=True)
    async def delcommand(self, ctx, *, command):
        """Removes restriction on [command] for all co-owners"""

        confirm = await self._confirm_owner(ctx)
        if not confirm:
            return

        if command in self.settings["RESTRICTED"]:
            await self.bot.say("**{}** has been removed from the restricted list".format(command))
            self.settings["RESTRICTED"].remove(command)
            dataIO.save_json(self.path, self.settings)
        elif command not in self.settings["RESTRICTED"]:
            await self.bot.say("{} is not a restricted command".format(command))
        else:
            await self.bot.say("{} is not a valid command.".format(command))

    @restrict.command(pass_context=True)
    async def adduser(self, ctx, user: discord.User,  *, command):
        """Restrict user from using [command]"""

        confirm = await self._confirm_owner(ctx)
        if not confirm:
            return

        AliasCog = self.bot.get_cog('Alias')
        server = ctx.message.server
        valid = True if self.bot.get_command(command) else False
        if not valid:
            valid = True if command in AliasCog.aliases[server.id] else False

        if user and user.id in self.settings["USERS"]:
            pass
        else:
            await self.bot.say("That user is not a co-owner.")
            return

        if valid and command not in self.settings["USERS"][user.id]["RESTRICTED"]:
            await self.bot.say("**{} will be restricted from using**: {}".format(user.display_name, command))
            self.settings["USERS"][user.id]["RESTRICTED"].append(command)
            dataIO.save_json(self.path, self.settings)
        elif command in self.settings["RESTRICTED"]:
            await self.bot.say("{} is already a restricted command for {}".format(command, user.display_name))
        else:
            await self.bot.say("{} is not a valid command.".format(command))

    @restrict.command(pass_context=True)
    async def deluser(self, ctx, user: discord.User, *, command):
        """Removes restriction on [command] for [user]"""

        confirm = await self._confirm_owner(ctx)
        if not confirm:
            return

        if user and user.id in self.settings["USERS"]:
            pass
        else:
            await self.bot.say("That user is not a co-owner.")
            return

        if command in self.settings["USERS"][user.id]["RESTRICTED"]:
            await self.bot.say("**{}** has been removed from {}'s' restricted list".format(command, user.display_name))
            self.settings["USERS"][user.id]["RESTRICTED"].remove(command)
            dataIO.save_json(self.path, self.settings)
        elif command not in self.settings["USERS"][user.id]["RESTRICTED"]:
            await self.bot.say("{} is not a restricted command for {}".format(command, user.display_name))
        else:
            await self.bot.say("{} is not a valid command.".format(command))
        pass

    @restrict.command(aliases=['wl'], pass_context=True)
    async def whitelist(self, ctx, cogname: str=None):
        """Whitelist all commands from a cog"""
        await self.bot.say("```fix\nWARNING: Enabling whitelist will disable blacklist if it is enabled\n```")
        confirm = await self._confirm_owner(ctx)
        if not confirm:
            return

        cog = cogname if self.bot.get_cog(cogname) else None
        if cog:
            self.settings["WL_ENABLED"] = True
            self.settings["BL_ENABLED"] = False
            self.settings["WHITELIST"].append(cogname)
            dataIO.save_json(self.path, self.settings)
            await self.bot.say("I have whitelisted all commands for **{}**".format(cog))
        elif cogname == None and len(self.settings["WHITELIST"]) > 0:
            self.settings["WL_ENABLED"] = not self.settings["WL_ENABLED"]
            await self.bot.say("**Whitelist enabled**: {}".format(self.settings["WL_ENABLED"]))
            dataIO.save_json(self.path, self.settings)
        elif cogname == None and len(self.settings["WHITELIST"]) < 1:
            await self.bot.say("I couldn't toggle whitelist on because you don't have any cogs whitelisted.")
        else:
            await self.bot.say("I couldn't find that cog")

    @restrict.command(aliases=['delwl'], pass_context=True)
    async def delwhitelist(self, ctx, cogname: str):
        """Remove a whitelisted cog"""
        confirm = await self._confirm_owner(ctx)
        if not confirm:
            return

        if not self.settings["WL_ENABLED"]:
            await self.bot.say("You don't have any cogs whitelisted.")
        elif cogname in self.settings["WHITELIST"]:
            self.settings["WHITELIST"].remove(cogname)
            if len(self.settings["WHITELIST"]) < 1:
                self.settings["WL_ENABLED"] = False
            dataIO.save_json(self.path, self.settings)
            await self.bot.say("**{}** removed from whitelist".format(cogname))
        else:
            await self.bot.say("That cog is not whitelisted or does not exist.")
        return

    @restrict.command(aliases=['bl'], pass_context=True)
    async def blacklist(self, ctx, cogname:  str=None):
        """Blacklist all commands from a cog"""

        await self.bot.say("```fix\nWARNING: Enabling blacklist will disable whitelist if it is enabled\n```")
        confirm = await self._confirm_owner(ctx)
        if not confirm:
            return

        cog = cogname if self.bot.get_cog(cogname) else None
        if cog:
            self.settings["BL_ENABLED"] = True
            self.settings["WL_ENABLED"] = False
            self.settings["BLACKLIST"].append(cogname)
            dataIO.save_json(self.path, self.settings)
            await self.bot.say("I have blacklisted all commands for **{}**".format(cog))
        elif cogname == None and len(self.settings["BLACKLIST"]) > 0:
            self.settings["BL_ENABLED"] = not self.settings["BL_ENABLED"]
            await self.bot.say("**Blacklist enabled**: {}".format(self.settings["BL_ENABLED"]))
            dataIO.save_json(self.path, self.settings)
        elif cogname == None and len(self.settings["BLACKLIST"]) < 1:
            await self.bot.say("I couldn't toggle whitelist on because you don't have any cogs whitelisted.")
        else:
            await self.bot.say("I couldn't find that cog")

    @restrict.command(aliases=['delbl'],pass_context=True)
    async def  delblacklist(self, ctx, cogname: str):
        """Remove a blacklisted cog"""

        confirm = await self._confirm_owner(ctx)
        if not confirm:
            return

        if not self.settings["BL_ENABLED"]:
            await self.bot.say("You don't have any cogs blacklisted.")
        elif cogname in self.settings["BLACKLIST"]:
            self.settings["BLACKLIST"].remove(cogname)
            if len(self.settings["BLACKLIST"]) < 1:
                self.settings["BL_ENABLED"] = False
            dataIO.save_json(self.path, self.settings)
            await self.bot.say("**{}** removed from blacklist".format(cogname))
        else:
            await self.bot.say("That cog is not blacklisted or does not exist.")
        return

    async def _confirm_owner(self, ctx):
        owner = discord.utils.get(self.bot.get_all_members(), id=self.bot.settings.owner)
        await self.bot.say("Please confirm you are the owner by typing **`yes`**")
        msg = await self.bot.wait_for_message(timeout=20, author=ctx.message.author, channel=ctx.message.channel)
        if msg == None:
            await self.bot.say("Cancelled")
            return False
        if msg.author != owner:
            await self.bot.say(random.choice(["You are not the owner! There is trickery afoot", "Scram!", "Shoo, you're annoying me", ":thinking: I'm offended at how gullible you think I am"]))
            return False
        elif msg.author == owner and msg.content == 'yes':
            return True
        return False # I don't know when this would trigger but return False just to be safe

def check_folders():
    paths = ["data/Sitryk-Cogs/coowner"]
    for path in paths:
        if not os.path.exists(path):
            print("Creating {} folder...".format(path))
            os.makedirs(path)


def check_files():
    f = "data/Sitryk-Cogs/coowner/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating empty settings.json...")
        dataIO.save_json(f, DEFAULT_SETTINGS)


def setup(bot):
    check_folders()
    check_files()
    n = CoOwner(bot)
    bot.add_cog(n)
