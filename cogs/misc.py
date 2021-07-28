import asyncio
import datetime
import logging
import random

import aiohttp
from discord import Embed
from discord.ext import commands
import timeago

module_logger = logging.getLogger('trashbot.MiscCog')


class MiscCog(commands.Cog):
    def __init__(self, bot):
        module_logger.info("initializing MiscCog")
        self.bot = bot
        self.logger = module_logger

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        module_logger.debug(f"user updated {before}")
        guild_state = self.bot.state.get_guild_state_by_id(before.guild.id)
        if after.id in guild_state.forced_nicks:
            forced_nick = guild_state.forced_nicks[after.id]["nick"]
            if after.nick != forced_nick:
                await after.edit(nick=guild_state.forced_nicks[after.id]["nick"])

    @commands.command(name="kik", hidden=True)
    async def whomst(self, ctx):
        now = datetime.datetime.now()
        guild_state = self.bot.state.get_guild_state_by_id(ctx.message.guild.id)
        t_locale = random.choice(['zh_CN', 'hu', 'en'])
        if self.bot.user.mentioned_in(ctx.message):
            embed = Embed(title="kb ezek vagy nemtom", color=0xFF5733)
            event_list_str = []

            if len(guild_state.last_vc_events):
                for r in list(reversed(guild_state.last_vc_events)):
                    event_str = """"""
                    user = r.user.nick if r.user.nick is not None else r.user.name
                    when = datetime.datetime.fromtimestamp(r.when)
                    event_str = event_str + f"`[{timeago.format(when, now, t_locale)}] "
                    if r.event:
                        event_str = event_str + f"""{user} jött ide: {r.channel.name}`"""
                    else:
                        event_str = event_str + f"""{user} ment a g*ecibe`"""
                    event_list_str.append(event_str)
            else:
                when = ctx.bot.globals.startup_at
                event_str = f"`[{timeago.format(when, now, t_locale)}] {random.choice(['sz*rtak a világra engem', 'keltem fel'])}`"
                event_list_str.append(event_str)

            embed.add_field(name="\u200b", value="\n".join(event_list_str))

            embed.set_author(name="Kovács Tibor József", url="https://www.facebook.com/tibikevok.jelolj/",
                             icon_url="https://scontent-vie1-1.xx.fbcdn.net/v/t1.6435-9/122705023_1507933319399057_8489117913383885547_n.jpg?_nc_cat=104&ccb=1-3&_nc_sid=8bfeb9&_nc_ohc=qd6IIUpCXgkAX9YV1zV&_nc_ht=scontent-vie1-1.xx&oh=caabf0e1cd80b2ca930d7f143fe73a25&oe=60BE032E")

            await ctx.send(embed=embed)

    @commands.command(name="ki", hidden=True)
    async def who(self, ctx, *args):
        guild_state = self.bot.state.get_guild_state_by_id(ctx.message.guild.id)
        if self.bot.user.mentioned_in(ctx.message):
            last_events = guild_state.last_vc_events

            if not len(last_events):
                await ctx.send("nemtom most keltem nem figyeltem")
            else:
                question = " ".join(args).replace("?", "").strip()

                if len(args) == 0:
                    last_event = last_events[-1]

                    await ctx.send(
                        f"{random.choice(['ö', 'nem vok spicli de ö', 'sztem ö'])}" +
                        f"{random.choice(['t láttam asszem feljönni', ' jött erre']) if last_event.event else ' lépett le'}: " +
                        f"{last_event.user.name}"
                    )

                elif question in ["joinolt", "van itt", "jött fel", "van itt"]:
                    last_joined = next((event for event in last_events if event.event), None)
                    if last_joined is not None:
                        await ctx.send(
                            f"{random.choice(['talán én...de az is lehet hogy ő', 'ez a köcsög', 'ö', 'ha valaki akk ö'])}: {last_joined.user.name}"
                        )
                    else:
                        await ctx.send("senki...")

                elif question in ["volt az", "lépett ki", "lépett le", "dczett", "disconnectelt"]:
                    last_left = next((event for event in last_events if not event.event), None)
                    if last_left is not None:
                        await ctx.send(
                            f"{random.choice(['ez a köcsög', 'ö', 'ha valaki akk ö'])} lépett le: {last_left.user.name}"
                        )
                    else:
                        await ctx.send("senki...")

            if random.randrange(0, 5) > 2:
                await asyncio.sleep(5)
                await ctx.send('👀')

    @commands.command(name='say', aliases=['mondd'])
    async def say(self, ctx, *args):
        self.logger.info("command called: {}".format(ctx.command))
        await ctx.message.delete()
        await ctx.send(' '.join(args))

    @commands.command(name='impostor', hidden=True)
    async def impost(self, ctx, *args):
        await ctx.message.delete()
        if len(args) > 0:
            impostor = args[0]
        else:
            impostor = random.choice(ctx.message.channel.members).mention
        tmpl = f""".      　。　　　　•　    　ﾟ　　。
　　.　　　.　　　  　　.　　　　　。　　   。　.
 　.　　      。　        ඞ   。　    .    •
   •        {impostor} was the impostor.　 。　.
　 　　。　　 　　　　ﾟ　　　.　    　　　.
,　　　　.　 .　　       ."""
        await ctx.send(tmpl)

    @commands.command(name="kot")
    async def kot(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('http://aws.random.cat/meow') as r:
                if r.status == 200:
                    js = await r.json()
                    await ctx.send(js['file'])


def setup(bot):
    bot.add_cog(MiscCog(bot))
