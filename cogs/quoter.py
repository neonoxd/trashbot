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
		self.cfg = json.loads(open("resources/config/quote_config.json", "r", encoding="utf8").read())
		self.content = self.read_quotes()

	@commands.command(name='qr')
	async def quote_reload(self, ctx):
		self.logger.info("command called: {}".format(ctx.command))
		self.cfg = json.loads(open("resources/config/quote_config.json", "r", encoding="utf8").read())
		self.content = self.read_quotes()

	@commands.command(name='quote', aliases=['q'])
	async def quote(self, ctx, *args):
		self.logger.info("command called: {}".format(ctx.command))
		await ctx.message.delete()
		if len(args) > 0:
			await ctx.send(embed=self.embed_for(args[0], ctx))

	def read_quotes(self):
		self.logger.debug("reading quotes")
		content = {}
		for q_src_n in list(self.cfg.keys()):
			filepath = f'resources/lists/{self.cfg[q_src_n]["src_file"]}'
			if os.path.exists(filepath):
				with open(filepath, 'r', encoding="utf8") as file:
					content[self.cfg[q_src_n]['src']] = file.read().split("\n\n")

		return content

	def embed_for(self, page_name, ctx):
		pm = None
		for q_src_n in list(self.cfg.keys()):
			if "alias" in self.cfg[q_src_n]:
				if page_name in self.cfg[q_src_n]["alias"].split(","):
					pm = self.cfg[q_src_n]

		if pm is None:
			pm = self.cfg[page_name]

		src_text = random.choice(self.content[pm["src"]])

		clean_text = re.sub("#url#.+", "", src_text)
		src_url_match = re.search("#url#.+", src_text)

		embed = discord.Embed(description=clean_text, title="", color=int(pm["color"], 16))

		if src_url_match is not None:
			embed.set_image(url=src_url_match[0].split("#url#")[1])

		embed.set_author(name=pm["name"], url=pm["url"], icon_url=pm["pfp"])
		embed.set_footer(text=f"Generázva neki: {ctx.message.author}")
		return embed


def setup(bot):
	bot.add_cog(QuoterCog(bot))
