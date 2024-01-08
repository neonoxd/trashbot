import asyncio
import datetime
import json
import os
import random
import string
from typing import List

import matplotlib.font_manager as fontman
from discord import TextChannel

from utils.state import TrashBot


def todo(logger, msg):
	logger.warn(f'TODO: {msg}')


def has_link(text):
	import re
	# findall() has been used
	# with valid conditions for urls in string
	regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
	url = re.findall(regex, text)
	return [x[0] for x in url]


def create_alphanumeric_string(length):
	return ''.join(random.sample(string.ascii_letters + string.digits, length))


def replace_str_index(text, index=0, replacement=''):
	return '%s%s%s' % (text[:index], replacement, text[index + 1:])


def get_user_nick_or_name(member):
	return member.nick if member.nick is not None else member.name


def find_member_by_id(guild, member_id):
	for member in guild.members:
		if member.id == int(member_id):
			return member


def find_font_file(query):
	matches = list(filter(lambda path: query in os.path.basename(path), fontman.findSystemFonts()))
	return matches


def get_resource_name_or_user_override(res_path):
	usrp = f"usr/{res_path}"
	resp = f"resources/{res_path}"
	return usrp if os.path.isfile(usrp) else resp


async def schedule_real_comedy(robot: TrashBot, channel: TextChannel):
	from cogs.bereal import trigger_real_comedy
	now = datetime.datetime.now()
	target = get_next_run_time()
	print(f"scheduled comedy @ {target}")
	await asyncio.sleep((target - now).total_seconds())
	await trigger_real_comedy(robot, channel)


def get_next_run_time_debug():
	return datetime.datetime.now() + datetime.timedelta(seconds=5)


def get_next_run_time():
	now = datetime.datetime.today()
	tomorrow = now + datetime.timedelta(days=1)
	return datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, random.randint(9, 22), random.randint(0, 59))


def load_goofies(bot):
	with open(get_resource_name_or_user_override("config/goofies.json"), 'r', encoding="utf8") as file:
		bot.globals.goofies = json.loads(file.read())
		for b_key in list(bot.globals.goofies.keys()):
			bot.globals.goofies[b_key] = int(bot.globals.goofies[b_key])


async def get_image_as_bytes(image_url):
	import aiohttp
	async with aiohttp.ClientSession() as session:
		async with session.get(image_url) as r:
			if r.status == 200:
				return await r.content.read()


def create_autocomplete_source(source: List, current_search: str):
	from discord import app_commands
	return [
		app_commands.Choice(name=choice, value=choice)
		for choice in source if current_search.lower() in choice.lower()
	]