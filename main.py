import asyncio
import json
import logging
import os
import random
import traceback
from os import listdir
from os.path import isfile, join

import aiocron
import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils.helpers import get_resource_name_or_user_override, schedule_real_comedy
from utils.state import BotState, BotConfig, TrashBot

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

logger = logging.getLogger('trashbot')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('bot.log', 'w', 'utf-8')
ch = logging.StreamHandler()

ch.setLevel(logging.DEBUG)
fh.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)


def get_prefix(command_bot, message):
	"""A callable Prefix for our bot. This could be edited to allow per server prefixes."""

	prefixes = ['k!']

	if not message.guild:
		return '?'

	return commands.when_mentioned_or(*prefixes)(command_bot, message)


cogs_dir = "cogs"

intents = discord.Intents.all()


bot = TrashBot(command_prefix=get_prefix, intents=intents)
bot.logger = logger


async def setup_state():
	bot.state = BotState()
	bot.globals = BotConfig(
		ph_token=os.getenv("PHTOKEN"),
		yt_cookie=os.getenv("YTCOOKIE"),
		ffmpeg_path=os.getenv("FFMPEG_PATH"),
		sounds_path=os.getenv("SNDS_PATH")
	)

	with open(get_resource_name_or_user_override("config/goofies.json"), 'r', encoding="utf8") as file:
		bot.globals.goofies = json.loads(file.read())
		for b_key in list(bot.globals.goofies.keys()):
			bot.globals.goofies[b_key] = int(bot.globals.goofies[b_key])

	with open(get_resource_name_or_user_override("lists/slur.list"), 'r', encoding="utf8") as file:
		bot.globals.slurs = file.readlines()

	with open(get_resource_name_or_user_override("lists/status.list"), 'r', encoding="utf8") as file:
		bot.globals.statuses = file.readlines()

	bot.globals.t_states = [
		"A horrible chill goes down your spine...", "Screams echo around you...", "Eater of Worlds has awoken!"
	]

	bot.globals.ghost_ids = [int(ghost_id) for ghost_id in os.getenv("GHOST_IDS").split(",")] if os.getenv(
		"GHOST_IDS") is not None \
		else []


async def setup_cogs():
	# load cogs

	debug_load_cogs = os.getenv("DEBUG_LOAD_COGS").split(",") if os.getenv(
		"DEBUG_LOAD_COGS") is not None else []

	for extension in [
		f.replace('.py', '') for f in listdir(cogs_dir)
		if isfile(join(cogs_dir, f)) and (len(debug_load_cogs) == 0 or f.replace('.py', '') in debug_load_cogs)
	]:
		try:
			await bot.load_extension(cogs_dir + "." + extension)
		except (discord.ClientException, ModuleNotFoundError):
			logger.error(f'Failed to load extension {extension}.')
			traceback.print_exc()


async def main():
	async with bot:
		await setup_state()
		await setup_cogs()
		await bot.start(TOKEN)


@bot.event
async def on_ready():
	from cogs.impl.shitpost_impl import think
	ver = os.popen("git rev-parse --short HEAD").read()
	bot.globals.verinfo["Tibi"] = ver
	bot.globals.verinfo["discord.py"] = discord.__version__
	bot.globals.verinfo["Bot User"] = bot.user.name
	bot.globals.verinfo["Bot ID"] = bot.user.id

	logger.debug(f'\n\n'
				 f'Logged in as: {bot.user.name} - {bot.user.id}\n'
				 f'Version: {discord.__version__}\n'
				 f'Running on commit: {ver}')

	await bot.change_presence(activity=discord.Game(
		random.choice(bot.globals.statuses)
	))

	logger.debug(f'Setting up state for {len(bot.guilds)} guilds')

	for guild in bot.guilds:
		bot.state.track_guild(guild.id)
		bot.loop.create_task(think(bot, guild.system_channel))
		bot.loop.create_task(schedule_real_comedy(bot, guild.system_channel))
		await guild.system_channel.send("na re")

	logger.debug(f'Successfully logged in and booted...!')


@aiocron.crontab('0 14 * * *')  # 14:00
async def trigger_cron():
	from cogs.impl.shitpost_impl import set_daily_tension
	await set_daily_tension(bot)


@aiocron.crontab("0 20 * * FRI")
async def trigger_friday_mfs():
	from cogs.impl.shitpost_impl import announce_friday_mfs
	await announce_friday_mfs(bot)


@aiocron.crontab('0 1 * * *')  # 01:00
async def reset_alert_states():
	from cogs.impl.shitpost_impl import reset_alert_states
	await reset_alert_states(bot)


@aiocron.crontab('0 12 * * *')  # 12:00
async def motd():
	from cogs.quoter import send_motd
	await send_motd(bot)


if __name__ == '__main__':
	asyncio.get_event_loop().run_until_complete(main())
