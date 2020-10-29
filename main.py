import json
import os
import logging
import random

import discord
from discord.ext import commands

from os import listdir
from os.path import isfile, join

import sys, traceback
from dotenv import load_dotenv

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
	bot.cvars = {}
	bot.cvars["PHTOKEN"] = PHTOKEN
	bot.cvars["state"] = {"guild": {}, "global": {}}

	with open('resources/db.json', 'r', encoding="utf8") as file:
		dbjson = json.loads(file.read())

	bot.cvars["slurps"] = {"slurs": [dbjson["slurs"][k]["slur"] for k in dbjson["slurs"]],
						   "chances": [dbjson["slurs"][k]["chance"] for k in dbjson["slurs"]]}
	bot.cvars["statuses"] = {"statuses": [dbjson["statuses"][k]["status"] for k in dbjson["statuses"]],
							 "chances": [dbjson["statuses"][k]["chance"] for k in dbjson["statuses"]]}

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
		random.choices(population=bot.cvars["statuses"]["statuses"], weights=bot.cvars["statuses"]["chances"])[0]
	))

	logger.debug(f'Successfully logged in and booted...!')


bot.run(TOKEN)
