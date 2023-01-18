import asyncio
import json
import logging
import os.path
import typing
from datetime import datetime

import discord.utils
from discord import Member
from discord.ext import commands
from discord.ext.commands import Context
from tabulate import tabulate

from utils.helpers import get_user_nick_or_name
from utils.state import TrashBot

module_logger = logging.getLogger('trashbot.WarnerCog')
warnpath = "usr/warns.json"


def read_warns():
	if not os.path.isfile(warnpath):
		with open(warnpath, "w") as f:
			f.write("{}")
			return {}
	else:
		with open(warnpath, "r") as f:
			return json.loads(f.read())


class WarnerCog(commands.Cog):
	def __init__(self, bot: TrashBot):
		self.bot = bot
		self.logger = module_logger
		module_logger.info(f"initializing {self.__cog_name__}")
		self.warns = read_warns()

	@commands.command(name='warn')
	async def warn(self, ctx: Context, member: Member, *reason_sep: str):
		reason = ' '.join(reason_sep)
		async with ctx.typing():
			module_logger.debug(f"{ctx.message.author} warns {member} for {reason}")
			if len(reason) > 150:
				await ctx.message.reply("ennyit nem tok megjegyezni báttya")
			else:
				await self.save_warn(ctx, member, reason)

	@commands.command(name='warns')
	async def warns(self, ctx: Context, member: typing.Union[Member, str, None]):
		module_logger.info(f"EEEE: {member}, {type(member)}")
		who = str(member.id) if member not in [None, "all"] else str(ctx.author.id)
		warns = "nicse"

		if member == "all":
			ids = list(self.warns.keys())
			all_warns = []
			for warned_id in ids:
				usr_warns = self.warns[warned_id]
				edited_warns = [[*warn, get_user_nick_or_name(discord.utils.get(ctx.bot.get_all_members(), id=int(warned_id)))] for warn in usr_warns]
				all_warns += edited_warns

			warn_string = self.format_warns_all(all_warns)
			warns = self.split_warns(warn_string)
		elif who in self.warns:
			warn_string = self.format_warns(self.warns[who])
			warns = self.split_warns(warn_string)

		if warns == "nicse":
			await ctx.message.reply(warns)
		else:
			await ctx.message.reply(f"hát\n```{warns[0]}```")

			for warn in warns[1:]:
				await asyncio.sleep(1)
				await ctx.message.reply(f"s még\n```{warn}```")

	@staticmethod
	def format_warns(warns):
		headers = ["KI", "MIKO", "MER"]
		data = [[warn[0], datetime.fromtimestamp(warn[2]).strftime('%Y-%m-%d %H:%M:%S'), warn[1]] for warn in warns]
		tabbed = tabulate(data, headers=headers, showindex=True)
		return tabbed

	@staticmethod
	def format_warns_all(warns):
		headers = ["KI", "KIT", "MIKO", "MER"]
		data = [[warn[0], warn[3], datetime.fromtimestamp(warn[2]).strftime('%Y-%m-%d %H:%M:%S'), warn[1]] for warn in warns]
		tabbed = tabulate(data, headers=headers, showindex=True)
		return tabbed

	@staticmethod
	def split_warns(tabbed):
		splitted = tabbed.split("\n")
		msgs = []
		out = ""
		for line in splitted:
			temp = out + line + "\n"
			if len(temp) > 2000:
				msgs.append(out)
				out = splitted[0] + "\n" + splitted[1] + "\n"
				out += line + "\n"
			else:
				out = temp

		if out != splitted[0] + "\n" + splitted[1] + "\n":
			msgs.append(out)
		return msgs

	async def save_warn(self, ctx, member, reason):
		who = str(member.id)
		warn = [ctx.message.author.name, reason, datetime.now().timestamp()]
		if who in self.warns:
			self.warns[who].append(warn)
		else:
			self.warns[who] = [warn]
		print(self.warns)
		with open(warnpath, "w") as f:
			f.write(json.dumps(self.warns))
		module_logger.info("saved warn")
		await ctx.message.reply("megjegyeztem 😂")


async def setup(bot: TrashBot):
	await bot.add_cog(WarnerCog(bot))
