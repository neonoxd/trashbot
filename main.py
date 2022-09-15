import json
import os
import logging
import random
import aiocron
import discord
from discord.ext import commands
from os import listdir
from os.path import isfile, join
import traceback
from dotenv import load_dotenv

from cogs.impl.shitpost import announce_friday_mfs
from utils.state import BotState, BotConfig

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

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=get_prefix, intents=intents)

if __name__ == '__main__':

	bot.state = BotState()
	bot.globals = BotConfig(
		ph_token=os.getenv("PHTOKEN"),
		yt_cookie=os.getenv("YTCOOKIE"),
		ffmpeg_path=os.getenv("FFMPEG_PATH"),
		sounds_path=os.getenv("SNDS_PATH"),
		sz_id=int(os.getenv("SZ_ID")),
		p_id=int(os.getenv("P_ID")),
		g_id=int(os.getenv("G_ID")),
		gba_id=int(os.getenv("GBA_ID")),
		cz_id=int(os.getenv("CZ_ID")),
		dzs_id=int(os.getenv("DZS_ID")),
		d_id=int(os.getenv("D_ID")),
		m_id=int(os.getenv("M_ID")),
		l_id=int(os.getenv("L_ID"))
	)

	slur_path = 'usr/lists/slur.list' if os.path.isfile('usr/lists/slur.list') else 'resources/lists/slur.list'
	with open(slur_path, 'r', encoding="utf8") as file:
		slur_list = file.readlines()

	status_path = 'usr/lists/status.list' if os.path.isfile('usr/lists/status.list') else 'resources/lists/status.list'
	with open(status_path, 'r', encoding="utf8") as file:
		status_list = file.readlines()

	bot.globals.slurs = slur_list
	bot.globals.statuses = status_list

	bot.globals.t_states = [
		"A horrible chill goes down your spine...", "Screams echo around you...", "Eater of Worlds has awoken!"
	]

	ghost_ids = [int(ghost_id) for ghost_id in os.getenv("GHOST_IDS").split(",")] if os.getenv("GHOST_IDS") is not None \
		else []

	bot.globals.ghost_ids = ghost_ids

	# load cogs

	debug_load_cogs = os.getenv("DEBUG_LOAD_COGS").split(",") if os.getenv("DEBUG_LOAD_COGS") is not None else []

	for extension in [
		f.replace('.py', '') for f in listdir(cogs_dir)
		if isfile(join(cogs_dir, f)) and (len(debug_load_cogs) == 0 or f.replace('.py', '') in debug_load_cogs)
	]:
		try:
			bot.load_extension(cogs_dir + "." + extension)
		except (discord.ClientException, ModuleNotFoundError):
			logger.error(f'Failed to load extension {extension}.')
			traceback.print_exc()


@bot.event
async def on_ready():
	logger.debug(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')

	await bot.change_presence(activity=discord.Game(
		random.choice(bot.globals.statuses)
	))

	logger.debug(f'Setting up state for {len(bot.guilds)} guilds')

	for guild in bot.guilds:
		from cogs.impl.shitpost import think
		bot.state.track_guild(guild.id)
		bot.loop.create_task(think(bot, guild.system_channel))

	logger.debug(f'Successfully logged in and booted...!')


@aiocron.crontab('0 14 * * *')  # 14:00
async def trigger_cron():
	from cogs.impl.shitpost import set_daily_tension
	await set_daily_tension(bot)


@aiocron.crontab("0 20 * * FRI")
async def trigger_friday_mfs():
	await announce_friday_mfs(bot)


@aiocron.crontab('0 1 * * *')  # 01:00
async def reset_alert_states():
	from cogs.impl.shitpost import reset_alert_states
	await reset_alert_states(bot)


bot.run(TOKEN)
