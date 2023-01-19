import asyncio
import json
import logging
import os.path
import traceback
import typing
from datetime import datetime
import random
from io import BytesIO

import discord.utils
from discord import Member
from discord.ext import commands
from discord.ext.commands import Context
from tabulate import tabulate

from utils.helpers import get_user_nick_or_name, find_member_by_id
from utils.state import TrashBot

module_logger = logging.getLogger('trashbot.WarnerCog')
warnpath = "usr/warns.json"


def read_warns():
	if not os.path.isfile(warnpath):
		with open(warnpath, "w", encoding="utf8") as f:
			f.write("{}")
			return {}
	else:
		with open(warnpath, "r", encoding="utf8") as f:
			return json.loads(f.read())


class WarnerCog(commands.Cog):
	def __init__(self, bot: TrashBot):
		self.bot = bot
		self.logger = module_logger
		module_logger.info(f"initializing {self.__cog_name__}")
		self.warns = read_warns()

	@commands.command(name='rw')
	async def reload_warns(self, ctx: Context):
		await ctx.message.delete()
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
		await asyncio.sleep(10)
		await ctx.message.delete()

	@commands.Cog.listener()
	async def on_command_error(self, ctx, err):
		module_logger.error(err)
		traceback.print_exception(err)

	@commands.command(name='warns')
	async def warns(self, ctx: Context, member: typing.Union[Member, str, None], dump=None):
		victim = str(member.id) if member not in [None, "all"] else str(ctx.author.id)

		warns = "nicse"

		if member == "all":
			module_logger.debug("dumping all warns")
			ids = list(self.warns.keys())
			all_warns = []
			for warned_id in ids:
				usr_warns = self.warns[warned_id]
				edited_warns = [
									[
										find_member_by_id(ctx.guild, warn[0]),
										*warn[1:],
										find_member_by_id(ctx.guild, warned_id)
									]
									for warn in usr_warns
								]
				all_warns += edited_warns
			all_warns = sorted(all_warns, key=lambda x: x[2])
			module_logger.debug(f"all_warns: {all_warns}")
			warn_string = self.format_warns_all(ctx, all_warns, dump)
			if dump:
				await ctx.message.reply("iesmik", file=discord.File(BytesIO(warn_string.encode()), "warns.csv"))
				return
			warns = self.split_warns(warn_string)

		elif victim in self.warns:
			all_warns = sorted(self.warns[victim], key=lambda x: x[2])
			warn_string = self.format_warns(ctx, all_warns)
			warns = self.split_warns(warn_string)

		if warns == "nicse":
			await ctx.message.reply(warns)
		else:
			await ctx.message.reply(f"hát\n```{warns[0]}```")

			for warn in warns[1:]:
				await asyncio.sleep(1)
				await ctx.message.reply(f"s még\n```{warn}```")

	@staticmethod
	def format_warns(ctx, warns):
		headers = ["KI", "MIKO", "MER"]
		data = [[find_member_by_id(ctx.guild, warn[0]), datetime.fromtimestamp(warn[2]).strftime('%Y-%m-%d %H:%M:%S'), warn[1]] for warn in warns]
		tabbed = tabulate(data, headers=headers, showindex=True)
		return tabbed

	@staticmethod
	def format_warns_all(ctx, warns, dump):
		module_logger.debug("dumping all warns")
		headers = ["KI", "KIT", "MIKO", "MER"]
		data = []

		for warn in warns:
			data.append([warn[0], warn[3],
			 datetime.fromtimestamp(warn[2]).strftime('%Y-%m-%d %H:%M:%S'), warn[1]])

		if dump:
			out = ";\t".join(headers)+"\n"
			for warnline in data:
				out += ";\t".join([str(warnparam) for warnparam in warnline])+"\n"
			return out
		else:
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

	async def save_warn(self, ctx: Context, member, reason):
		who = str(member.id)
		warn = [ctx.message.author.id, reason, datetime.now().timestamp()]
		if who in self.warns:
			self.warns[who].append(warn)
		else:
			self.warns[who] = [warn]
		with open(warnpath, "w", encoding="utf8") as f:
			f.write(json.dumps(self.warns, indent=4, ensure_ascii=False))
		module_logger.info("saved warn")
		msg = "megjegyeztem 😂"
		if len(self.warns[who]) > 2:
			msg += f" {random.choice(['má sokadik', 'de enyi', 'nem elsö'])} 😂 {len(self.warns[who])}"
		await ctx.message.reply(msg, delete_after=5)


async def setup(bot: TrashBot):
	await bot.add_cog(WarnerCog(bot))
