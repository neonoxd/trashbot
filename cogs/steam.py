import asyncio
import datetime
import logging
import os
import re
from re import Match
from typing import List

import aiohttp
import discord
from discord import app_commands, PrivacyLevel, EntityType
from discord.ext import commands

from utils.state import TrashBot
from utils.helpers import get_image_as_bytes

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
		self.logger.info(f"searching for {app_name}")
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
		return [res['name'] for res in result]

	async def steam_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
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
		if event is not None:
			await interaction.response.send_message(event.url)
		del self.last_results[interaction.user.id]

	async def create_event_for_app(self, app_search_data, interaction):
		app_id = app_search_data['appid']
		app_data = await self.search_app_by_id(app_search_data['appid'])

		if not app_data[app_id]["success"]:
			await interaction.response.send_message("vmi gyász")
			return None

		app_data_d = app_data[app_id]['data']
		app_data_release_date = app_data_d['release_date']

		is_coming_soon = app_data_release_date['coming_soon'] if 'coming_soon' in app_data_release_date else False
		if not is_coming_soon:
			await interaction.response.send_message("má kinvan sztem")
			return None

		release_date = await self.parse_date(app_data_d['release_date'])

		header_img_url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg"
		steam_page_url = f"https://store.steampowered.com/app/{app_id}"
		img_data = await get_image_as_bytes(header_img_url)

		event_data = {
			'name': app_data_d['name'],
			'app_id': app_id,
			'description': app_data_d['short_description'],
			'link': steam_page_url,
			'image': img_data
		}

		if release_date is None:
			await interaction.response.send_modal(DateFillModal(self, event_data))
			return None

		return await interaction.guild.create_scheduled_event(name=app_data_d['name'], start_time=release_date, end_time=release_date + datetime.timedelta(hours=1), description=str(app_data_d['short_description']), image=img_data, location=steam_page_url, entity_type=EntityType.external, privacy_level=PrivacyLevel.guild_only)

	async def parse_date(self, date) -> datetime.datetime:

		parsed_date: datetime.datetime | None = None

		date_str = date['date']

		q_regex: Match = re.match("(Q[1-4]) (\\d{4})", date_str)
		q_regex_year: Match = re.match("^\\d{4}$", date_str, flags=re.RegexFlag.MULTILINE)
		if q_regex:
			module_logger.info(f"Quarter date matched: {date_str}")
			quarter = int(q_regex.groups()[0][1])
			year = int(q_regex.groups()[1])
			parsed_date = datetime.datetime(year, quarter * 3, 1, hour=17, minute=0, tzinfo=datetime.timezone.utc)
		elif q_regex_year:
			module_logger.info(f"date matched: {date_str}")
			parsed_date = datetime.datetime(int(q_regex_year.group(0)), 12, 31, hour=17, minute=0, tzinfo=datetime.timezone.utc)
		else:
			try:
				parsed_date = datetime.datetime.strptime(date_str, '%d %b, %Y')
				parsed_date = parsed_date.replace(hour=17, minute=0, tzinfo=datetime.timezone.utc)
			except ValueError:
				self.logger.info(f"{date_str} is not parseable")

		return parsed_date


class DateFillModal(discord.ui.Modal, title='várjál tesomsz de ez miko?'):
	date_str = discord.ui.TextInput(label='igy', placeholder="nap Hón, év | Q1 2024 | 2024")

	def __init__(self, cog: SteamCog, event_data, timeout=180):
		super().__init__(timeout=timeout)
		self.cog = cog
		self.event_data = event_data

	async def on_submit(self, interaction: discord.Interaction):
		date_obj = {'coming_soon': True, 'date': self.date_str.value}
		parsed_date = await self.cog.parse_date(date_obj)
		from discord import EntityType
		event = await interaction.guild.create_scheduled_event(name=self.event_data['name'], start_time=parsed_date,
															  end_time=parsed_date + datetime.timedelta(hours=1),
															  description=self.event_data['description'],
															  image=self.event_data['image'], location=self.event_data['link'],
															  entity_type=EntityType.external,
															  privacy_level=PrivacyLevel.guild_only)
		await interaction.response.send_message(event.url)

	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		module_logger.error(error, exc_info=True)


async def setup(bot: TrashBot):
	await bot.add_cog(SteamCog(bot))
