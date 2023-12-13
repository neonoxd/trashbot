import datetime
import logging
import os
import re
from re import Match
from typing import List

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from utils.state import TrashBot

module_logger = logging.getLogger('trashbot.SteamCog')


class SteamCog(commands.Cog):

	def __init__(self, bot: TrashBot):
		self.bot = bot
		self.logger = module_logger
		self.apikey = os.getenv("STEAM_APIKEY")
		self.last_results = {}

	async def search_app_by_name(self, app_name: str):
		if app_name == "" or app_name is None or len(app_name) == 1:
			return []
		url = "https://steamcommunity.com/actions/SearchApps/"
		search_url = url + app_name
		async with aiohttp.ClientSession() as session:
			async with session.get(search_url) as r:
				if r.status == 200:
					data = await r.json()
					self.logger.info(f"Search results for {app_name}")
					self.logger.info(data)
					return data
				else:
					return []

	async def search_app_by_id(self, app_id: int):
		url = "https://store.steampowered.com/api/appdetails/"
		param_name = "appids"
		param_value = app_id

		async with aiohttp.ClientSession() as session:
			async with session.get(url, params={param_name: param_value}) as r:
				if r.status == 200:
					data = await r.json()
					self.logger.info(f"Search results for {app_id}")
					self.logger.info(data)
					return data

	async def _search(self, app_name: str, user_id: int):
		result = await self.search_app_by_name(app_name)
		self.last_results[user_id] = {res['name']: res for res in result}
		self.logger.info(f"last_results: {len(self.last_results)}")
		return [res['name'] for res in result]

	async def steam_autocomplete(self, interaction: discord.Interaction, current: str) \
			-> List[app_commands.Choice[str]]:
		self.logger.info(f"{interaction.user.id} searching for {current}")
		choices = await self._search(current, interaction.user.id)
		return [
			app_commands.Choice(name=choice, value=choice)
			for choice in choices
		]

	@app_commands.command(name="steamsearch")
	@app_commands.autocomplete(app_name=steam_autocomplete)
	async def slash_steamsearch(self, interaction: discord.Interaction, app_name: str):
		store_url = "https://store.steampowered.com/app/"
		app_data = self.last_results[interaction.user.id][app_name]
		store_link = store_url + app_data['appid']
		await interaction.response.send_message(store_link)

	@app_commands.command(name="steamevent")
	@app_commands.autocomplete(app_name=steam_autocomplete)
	async def slash_steamevent(self, interaction: discord.Interaction, app_name: str):
		app_search_data = self.last_results[interaction.user.id][app_name]
		event = await self.create_event_for_app(app_search_data, interaction)
		await interaction.response.send_message(event.url)

	async def create_event_for_app(self, app_search_data, interaction):
		from utils.helpers import get_image_as_bytes
		from discord import EntityType
		from discord import PrivacyLevel

		app_id = app_search_data['appid']
		app_data = await self.search_app_by_id(app_search_data['appid'])
		app_data_d = app_data[app_id]['data']

		header_img_url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg"
		steam_page_url = f"https://store.steampowered.com/app/{app_id}"
		release_date_notz = await self.parse_date(app_data_d['release_date'])
		release_date = datetime.datetime.combine(release_date_notz, datetime.datetime.min.time(), datetime.timezone.utc)

		img_data = await get_image_as_bytes(header_img_url)
		event = await interaction.guild.create_scheduled_event(name=app_data_d['name'], start_time=release_date, end_time=release_date + datetime.timedelta(hours=1), description=str(app_data_d['short_description']), image=img_data, location=steam_page_url, entity_type=EntityType.external, privacy_level=PrivacyLevel.guild_only)
		return event

	async def parse_date(self, date):

		parsed_date: datetime.date | None = None

		date_str = date['date']

		q_regex: Match = re.match("(Q[1-4]) (\\d{4})", date_str)
		q_regex_year: Match = re.match("^\\d{4}$", date_str, flags=re.RegexFlag.MULTILINE)
		if q_regex:
			module_logger.info(f"Quarter date matched: {date_str}")
			quarter = int(q_regex.groups()[0][1])
			year = int(q_regex.groups()[1])
			parsed_date = datetime.date(year, quarter * 3, 1)
		elif q_regex_year:
			module_logger.info(f"date matched: {date_str}")
			parsed_date = datetime.date(int(q_regex_year.group(0)), 12, 31)
		else:
			try:
				parsed_date = datetime.datetime.strptime(date_str, '%d %b, %Y')
			except ValueError:
				self.logger.info(f"{date_str} is not parseable")

		return parsed_date


async def setup(bot: TrashBot):
	await bot.add_cog(SteamCog(bot))
