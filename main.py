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
from utils.state import BotState, BotConfig

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PHTOKEN = os.getenv("PHTOKEN")

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


def get_prefix(bot, message):
	"""A callable Prefix for our bot. This could be edited to allow per server prefixes."""

	# Notice how you can use spaces in prefixes. Try to keep them simple though.
	prefixes = ['k!']

	# Check to see if we are outside of a guild. e.g DM's etc.
	if not message.guild:
		# Only allow ? to be used in DMs
		return '?'

	# If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
	return commands.when_mentioned_or(*prefixes)(bot, message)


cogs_dir = "cogs"

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=get_prefix, intents=intents)

if __name__ == '__main__':

	bot.state = BotState()
	bot.globals = BotConfig(
		ph_token=PHTOKEN,
		ffmpeg_path=os.getenv("FFMPEG_PATH"),
		sounds_path=os.getenv("SNDS_PATH"),
		sz_id=int(os.getenv("SZ_ID")),
		p_id=int(os.getenv("P_ID"))
	)

	with open('resources/lists/slur.list', 'r', encoding="utf8") as file:
		slur_list = file.readlines()

	with open('resources/lists/status.list', 'r', encoding="utf8") as file:
		status_list = file.readlines()

	bot.globals.slurs = slur_list
	bot.globals.statuses = status_list

	# load cogs
	for extension in [f.replace('.py', '') for f in listdir(cogs_dir) if isfile(join(cogs_dir, f))]:
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
		from cogs.shitpost import think
		bot.state.track_guild(guild.id)
		bot.loop.create_task(think(bot, guild.system_channel))

	logger.debug(f'Successfully logged in and booted...!')


@aiocron.crontab('0 14 * * *')  # 14:00
async def trigger_cron():
	from cogs.shitpost import set_daily_tension
	await set_daily_tension(bot)


@aiocron.crontab('0 1 * * *')  # 01:00
async def reset_alert_states():
	from cogs.shitpost import reset_alert_states
	await reset_alert_states(bot)


bot.run(TOKEN)
