import logging
import os
import random

import discord
import psycopg2
from discord.ext import commands
from dotenv import load_dotenv

import shared
from config import cfg
from utils import mercy_maybe, roll, handle_beemovie_command

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
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
PHToken = "92a95ab0a3f4d2de"
shared.init()
bot = commands.Bot(command_prefix=cfg["prefix"])


@bot.command(name='roll', description="guritok")
async def rollcmd(ctx, *args):
    await ctx.send(roll(args))


@bot.command(name='vandam', description="kinyirok mid ekit")
async def vandam(ctx, *args):
    logging.info("command called: {}".format(ctx.command))
    if len(args) > 0:
        await mercy_maybe(bot, ctx.channel, int(args[0]))
    else:
        await mercy_maybe(bot, ctx.channel)


@bot.command(name='captcha', description="random PH captcha")
async def captcha(ctx):
    logging.info("command called: {}".format(ctx.command))
    from utils import get_captcha
    cimg = await get_captcha(PHToken)
    await ctx.send(file=discord.File(cimg, 'geci.png'))

@bot.command(name='tenemos')
async def tenemos(ctx):
    logging.info("command called: {}".format(ctx.command))
    await ctx.send(file=discord.File('resources/tenemos.jpg'))

@bot.command(name='zene', description="random leg job zene idézet")
async def zene(ctx):
    logging.info("command called: {}".format(ctx.command))
    embed = discord.Embed(description="-Leg job zenék", title=random.choice(shared.trek_list), color=0xfc0303)
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


@bot.command(name='meh', description="elmondom afilmet röviden")
async def bee(ctx, *args):
    logging.info("command called: {}".format(ctx.command))
    await handle_beemovie_command(ctx, args)


@bot.command(name='trashwatch')
async def trashwatch(ctx, *args):
    logging.info("command called: {}".format(ctx.command))


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(
        random.choices(population=shared.statuses["statuses"], weights=shared.statuses["chances"])[0]
    ))
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
    await handle_on_message(bot, message)


bot.run(TOKEN)
