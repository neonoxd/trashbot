import asyncio
import datetime
import os
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv
from config import cfg
from utils import Slapper, check_streams
import shared
#import logging

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] %(message)s",
#     handlers=[
#         logging.StreamHandler()
#     ]
# )


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


@bot.command(name='trashwatch')
async def trashwatch(ctx, *args):
    await ctx.send("TrashWatch:tm: szabin van")
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
    print("ready")


@bot.event
async def on_typing(channel, user, when):
    from eventhandlers import handle_on_typing
    await handle_on_typing(bot, channel, user, when)

@bot.command(name='vandam', description="kinyirok mid ekit")
async def vandam(ctx, *args):
    await doraffle(ctx.channel, 60)

async def doraffle(channel,timeout = 30):
    print("raffle created with timeout %s" % timeout)
    raffle = {
        "msgid": None,
        "date": None,
        "users": []
    }

    def check(reaction, user):
        return reaction.message.id == raffle["msgid"]

    msg = await channel.send("A likolok közül kiválasztok egy szerencsés tulélöt, a töbi sajnos meg hal")
    raffle["msgid"] = msg.id
    raffle["date"] = datetime.datetime.now()
    raffle["users"] = []


    while (datetime.datetime.now() - raffle["date"]).total_seconds() < timeout:
        print("raffle time: {}".format((datetime.datetime.now() - raffle["date"]).total_seconds()))
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=10.0, check=check)
            raffle["users"].append(user.mention)
            print("got reacc {} {}".format(reaction, user))
            reaction, user = None, None
        except Exception as e:
            pass
    print("raffle ended")
    raffle["active"] = False
    if (len(raffle["users"]) > 0):
        await channel.send("az egyetlen tul élö {}".format(random.choice(raffle["users"])))
    else:
        await channel.send("sajnos senki nem élte tul")


async def think(message):
    channel = message.channel

    while True:
        print("thought")
        roll = random.randrange(0, 1000)
        if roll < 5:
            print("rolled %s" % roll)
            await doraffle(channel)
        elif roll < 10:
            print("rolled %s" % roll)
            channel.send("most majdnem ki nyirtam vkit")

        await asyncio.sleep(30)


@bot.event
async def on_message(message):
    from eventhandlers import handle_on_message
    if message.author == bot.user:
        return
    if not shared.state["thinkLoop"][0]:
        print("thinking activated")
        shared.state["thinkLoop"]= [True, message.channel.id]
        bot.loop.create_task(think(message))

    await handle_on_message(bot, message)


bot.run(TOKEN)
