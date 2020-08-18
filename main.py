import datetime
import os
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv
from config import cfg
from utils import Slapper, check_streams
import shared

shared.init()
bot = commands.Bot(command_prefix=cfg["prefix"])
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PHToken = "92a95ab0a3f4d2de"


@bot.command(name='hal')
async def slap(ctx, *, reason: Slapper):
    await ctx.send(reason)


@bot.command(name='captcha', description="random PH captcha")
async def captcha(ctx):
    from utils import get_captcha
    cimg = await get_captcha(PHToken)
    await ctx.send(file=discord.File(cimg, 'geci.png'))


@bot.command(name='zene', description="random leg job zene idézet")
async def zene(ctx):
    embed = discord.Embed(description="-Leg job zenék", title=random.choice(shared.legjob_zene_list), color=0xfc0303)
    await ctx.send(embed=embed)


@bot.command(name='arena', description="ketrecharc bunyo, hasznalat: {0}arena @user1 @user2 ...".format(cfg["prefix"]))
async def fight(ctx, *args):
    if len(args) == 0:
        return
    await ctx.send("a ketrec harc gyöz tese: {}".format(random.choice(args)))


@bot.command(name='say', description="bemondom ha irsz utana valamit")
async def say(ctx, *args):
    await ctx.send(' '.join(args))


@bot.command(name='trashpolice')
async def trashwatch(ctx, *args):
    return
    if ctx.channel.id in shared.state["attachedChannels"]:
        curstatus = shared.state["attachedChannels"][ctx.channel.id]["attached"]
        shared.state["attachedChannels"][ctx.channel.id]["attached"] = not curstatus
        shared.state["attachedChannels"][ctx.channel.id]["when"] = datetime.datetime.now()
    else:
        shared.state["attachedChannels"][ctx.channel.id] = {"attached": True, "when": datetime.datetime.now()}
        print("adding stream checker bot loop task")
        bot.loop.create_task(check_streams(ctx))

    await ctx.send("TrashWatch {}".format(shared.state["attachedChannels"][ctx.channel.id]["attached"]))



@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(random.choice(shared.statuses)))
    print("ready")


@bot.event
async def on_typing(channel, user, when):
    from eventhandlers import handle_on_typing
    await handle_on_typing(bot, channel, user, when)


@bot.event
async def on_message(message):
    from eventhandlers import handle_on_message
    if message.author == bot.user:
        return
    await handle_on_message(bot, message)


bot.run(TOKEN)
