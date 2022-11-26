import json
import logging
import os
import random
import re

import discord
from discord.ext import commands

module_logger = logging.getLogger('trashbot.QuoterCog')


class QuoterCog(commands.Cog):
	def __init__(self, bot):
		module_logger.info("initializing PinnerCog")
		self.logger = module_logger
		bot.state.quotecfg = json.loads(open("resources/config/quote_config.json", "r", encoding="utf8").read())
		bot.state.quotecontent = self.read_quotes()

	@commands.command(name='qr')
	async def quote_reload(self, ctx):
		self.logger.info("command called: {}".format(ctx.command))
		ctx.bot.state.quotecfg = json.loads(open("resources/config/quote_config.json", "r", encoding="utf8").read())
		ctx.bot.state.quotecontent = self.read_quotes()

	@commands.command(name='quote', aliases=['q'])
	async def quote(self, ctx, *args):
		self.logger.info("command called: {}".format(ctx.command))
		await ctx.message.delete()
		if len(args) > 0:
			await ctx.send(embed=self.embed_for(args[0], ctx.bot, ctx.message.author))

	@commands.command(name='motd')
	async def motd(self, ctx):
		self.logger.info("command called: {}".format(ctx.command))
		await ctx.message.delete()
		if ctx.bot.state.motd is not None:
			await ctx.send(embed=ctx.bot.state.motd)
		else:
			await send_motd(ctx.bot)

	def read_quotes(self):
		self.logger.debug("reading quotes")
		content = {}
		for q_src_n in list(ctx.bot.state.quotecfg.keys()):
			filepath = f'resources/lists/{ctx.bot.state.quotecfg[q_src_n]["src_file"]}'
			if os.path.exists(filepath):
				with open(filepath, 'r', encoding="utf8") as file:
					content[ctx.bot.state.quotecfg[q_src_n]['src']] = file.read().split("\n\n")

		return content

	@staticmethod
	def embed_for(page_name, bot, author):
		pm = None
		for q_src_n in list (bot.state.quotecfg.keys()):
			if "alias" in bot.state.quotecfg[q_src_n]:
				if page_name in bot.state.quotecfg[q_src_n]["alias"].split(","):
					pm = bot.state.quotecfg[q_src_n]

		if pm is None:
			pm = bot.state.quotecfg[page_name]

		src_text = random.choice(bot.state.quotecontent[pm["src"]])

		clean_text = re.sub("#url#.+", "", src_text)
		src_url_match = re.search("#url#.+", src_text)

		embed = discord.Embed(description=clean_text, title="", color=int(pm["color"], 16))

		if src_url_match is not None:
			embed.set_image(url=src_url_match[0].split("#url#")[1])

		embed.set_author(name=pm["name"], url=pm["url"], icon_url=pm["pfp"])
		embed.set_footer(text=f"Generázva neki: {author}")
		return embed


async def send_motd(bot):
	quotekeys = list(bot.state.quotecfg.keys())
	random_pagename = random.choice(quotekeys)
	cog = bot.get_cog('QuoterCog')
	embed = cog.embed_for(random_pagename, bot, 'KTJ')
	
	guild_state = bot.state.guilds[0]
	module_logger.debug(f'Sending MOTD for: {guild_state.id}')
	guild = discord.utils.get(bot.guilds, id=guild_state.id)
	channel = guild.system_channel
	await channel.send(embed=embed, content='MOTD - Message of the Day')
	bot.state.motd = embed


def setup(bot):
	bot.add_cog(QuoterCog(bot))
