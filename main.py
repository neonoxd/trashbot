import datetime
import os

from discord.ext import commands
from dotenv import load_dotenv
from config import cfg
import shared
import logging
import discord
from utils import Slapper, doraffle, think, roll, check_streams, get_trashwatch_youtube_list, beemovie_task
import random

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_URL = os.environ['DATABASE_URL']
PHToken = "92a95ab0a3f4d2de"
shared.init()
bot = commands.Bot(command_prefix=cfg["prefix"])


@bot.command(name='hal')
async def slap(ctx, *, reason: Slapper):
    logging.info("command called: {}".format(ctx.command))
    await ctx.send(reason)


@bot.command(name='roll', description="guritok")
async def rollcmd(ctx,*args):
    await ctx.send(roll(args))


@bot.command(name='vandam', description="kinyirok mid ekit")
async def vandam(ctx, *args):
    logging.info("command called: {}".format(ctx.command))
    if len(args) > 0:
        await doraffle(bot, ctx.channel, int(args[0]))
    else:
        await doraffle(bot, ctx.channel)


@bot.command(name='captcha', description="random PH captcha")
async def captcha(ctx):
    logging.info("command called: {}".format(ctx.command))
    from utils import get_captcha
    cimg = await get_captcha(PHToken)
    await ctx.send(file=discord.File(cimg, 'geci.png'))


@bot.command(name='zene', description="random leg job zene idézet")
async def zene(ctx):
    logging.info("command called: {}".format(ctx.command))
    embed = discord.Embed(description="-Leg job zenék", title=random.choice(shared.legjob_zene_list), color=0xfc0303)
    await ctx.send(embed=embed)


@bot.command(name='arena', description="ketrecharc bunyo, hasznalat: {0}arena @user1 @user2 ...".format(cfg["prefix"]))
async def fight(ctx, *args):
    logging.info("command called: {}".format(ctx.command))
    if len(args) == 0:
        return
    await ctx.send("a ketrec harc gyöz tese: {}".format(random.choice(args)))


@bot.command(name='say', description="bemondom ha irsz utana valamit")
async def say(ctx, *args):
    logging.info("command called: {}".format(ctx.command))
    await ctx.send(' '.join(args))

@bot.command(name='meh')
async def bee(ctx, *args):
    if ctx.channel.id in shared.state["beechannels"]:
        curstatus = shared.state["beechannels"][ctx.channel.id]["attached"]
        shared.state["beechannels"][ctx.channel.id]["attached"] = not curstatus
        shared.state["beechannels"][ctx.channel.id]["when"] = datetime.datetime.now()
        shared.state["beechannels"][ctx.channel.id]["current_page"] = 0
    else:
        shared.state["beechannels"][ctx.channel.id] = {"attached": True, "when": datetime.datetime.now(),
                                                       "current_page": 0}
        bot.loop.create_task(beemovie_task(ctx))

    if shared.state["beechannels"][ctx.channel.id]["attached"]:
        await ctx.send("szoval...")
    else:
        await ctx.send("na m1...")

@bot.command(name='trashwatch')
async def trashwatch(ctx, *args):
    logging.info("command called: {}".format(ctx.command))
    return
    if ctx.channel.id in shared.state["attachedChannels"]:
        curstatus = shared.state["attachedChannels"][ctx.channel.id]["attached"]
        shared.state["attachedChannels"][ctx.channel.id]["attached"] = not curstatus
        shared.state["attachedChannels"][ctx.channel.id]["when"] = datetime.datetime.now()
    else:
        shared.state["attachedChannels"][ctx.channel.id] = {"attached": True, "when": datetime.datetime.now()}
        print("adding stream checker bot loop task")
        bot.loop.create_task(check_streams(ctx))

    if shared.state["attachedChannels"][ctx.channel.id]["attached"]:
        await ctx.send("TrashWatch:tm: Bekapcsolva")
    else:
        await ctx.send("TrashWatch:tm: Kikapcsolva")


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(random.choice(shared.statuses)))
    logging.info("ready")


@bot.event
async def on_typing(channel, user, when):
    from eventhandlers import handle_on_typing
    await handle_on_typing(bot, channel, user, when)


@bot.event
async def on_message(message):
    from eventhandlers import handle_on_message
    if message.author == bot.user:
        return
    if not shared.state["thinkLoop"][0]:
        logging.info("thinking activated")
        shared.state["thinkLoop"] = [True, message.channel.id]
        bot.loop.create_task(think(bot, message))
    await handle_on_message(bot, message)

bot.run(TOKEN)