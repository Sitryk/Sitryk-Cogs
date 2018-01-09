import os
import discord
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import chat_formatting as cf
from .utils import checks
from copy import deepcopy
try:
    from tabulate import tabulate
    _have_tabulate = True
except:
    _have_tabulate = False
from __main__ import send_cmd_help


class InviteTrack:
    """A cog that tracks some invites"""

    def __init__(self, bot):
        self.bot = bot
        self.path = 'data/Sitryk-Cogs/invitetrack/settings.json'
        self.data = dataIO.load_json(self.path)

    @commands.group(pass_context=True, no_pm=True)
    @checks.mod_or_permissions()
    async def invites(self, ctx):
        """
        A little info on invites
        """
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @invites.command(pass_context=True, no_pm=True)
    async def list(self, ctx, show_codes: str='no_show'):
        """
        Lists active invites, do [p]invites list show, to show invite codes
        """
        try:
            server = ctx.message.server
            to_format = [['Code', 'Uses', 'Link Owner', 'Expires']]
            invites = [x for x in await self.bot.invites_from(server)]

            for invite in invites:
                code = invite.id if (show_codes == 'show') else 'X' * len(invite.id)
                uses = "{}/{}".format(invite.uses, invite.max_uses) if invite.max_uses else "{}".format(invite.uses)
                expiry = "True" if invite.max_age == 0 else "False"

                to_format.append([code, uses, invite.inviter.name, expiry])

            for page in cf.pagify(tabulate(to_format, headers="firstrow", showindex="always")):
                await self.bot.say(cf.box(page))
        except:
            await self.bot.say("I need the `Manage Server` permission to view invites.")

    @invites.command(pass_context=True, no_pm=True)
    async def info(self, ctx, invite_code: str):
        """Show info on an invitation"""
        server = ctx.message.server
        await self.check_invites(server)
        try:
            msg = ""
            for key, val in self.data[server.id][invite_code].items():
                if key == 'who_used':
                    users = []
                    for _id in self.data[server.id][invite_code]['who_used']:
                        user = await self.bot.get_user_info(_id)
                        users.append(str(user))
                    msg += "who_used: {}\n\n".format(", ".join(sorted(users)))
                else:
                    msg += "{}: {}\n".format(key, val)
            for page in cf.pagify(msg):
                await self.bot.say(cf.box(page))

        except (IndexError, KeyError):
            await self.bot.say("I don't have any info about that invitation code.")


    def save_data(self):
        dataIO.save_json(self.path, self.data)
        
    async def check_invites(self, server):
        try:
            if server.id not in self.data:
                self.data[server.id] = {}

            active_invites = [x for x in await self.bot.invites_from(server)]

            for invite in active_invites:
                if invite.id not in self.data[server.id]:
                    self.data[server.id][str(invite.id)] = {'active': invite.revoked,
                                                 'uses': invite.uses,
                                                 'max_uses': invite.max_uses,
                                                 'max_age': invite.max_age,
                                                 'channel': invite.channel.id,
                                                 'inviter': invite.inviter.id,
                                                 'created_at': str(invite.created_at),
                                                 'who_used': []
                                                }
                elif invite.id in self.data[server.id]:
                    self.data[server.id][str(invite.id)]['uses'] = invite.uses

            for invite_id in self.data[server.id]:
                if invite_id not in [i.id for i in active_invites]:
                    self.data[server.id][invite_id]['active'] = False

            self.save_data()
        except Exception as e:
            print(e)

    async def on_member_join(self, member):
        server = member.server
        try:
            old = copy(self.data[server.id])
            await self.check_invites(server)
            new = copy(self.data[server.id])

            for invite_id in old:
                if old[invite_id]['uses'] < new[invite_id]['uses']:
                    self.data[server.id][invite_id]['who_used'].append(member.id)
            self.save_data()
        except Exception as e:
            print(e)

        
def check_folders():
    if not os.path.exists('data/Sitryk-Cogs/invitetrack'):
        os.makedirs('data/Sitryk-Cogs/invitetrack')
        print()
        print('Sitryk-Cogs :     Writing new directory')
        print('Sitryk-Cogs :     data/Sitryk-Cogs/invitetrack')


def check_files():
    if not dataIO.is_valid_json('data/Sitryk-Cogs/invitetrack/settings.json'):
        dataIO.save_json('data/Sitryk-Cogs/invitetrack/settings.json', {})
        print()
        print('Sitryk-Cogs :     Writing new file to directory')
        print('Sitryk-Cogs :     data/Sitryk-Cogs/invitetrack/settings.json')


def setup(bot):
    if _have_tabulate:
        check_folders()
        check_files()
        n = InviteTrack(bot)
        bot.add_cog(n)
    else:
        raise RuntimeError("You need to run `pip3 install tabulate`")
