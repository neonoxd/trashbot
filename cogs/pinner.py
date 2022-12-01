import json
import logging
import os
import discord
from discord.ext.commands import Bot, Context

from utils.helpers import todo
from discord.ext import commands

module_logger = logging.getLogger('trashbot.PinnerCog')


class PinnerCog(commands.Cog):
	def __init__(self, bot: Bot):
		module_logger.info("initializing PinnerCog")
		pin_dir = 'usr'
		pin_fname = 'pins.json'
		self.pin_path = os.path.join(pin_dir, pin_fname)

		self.bot = bot
		self.logger = module_logger
		self.pins = {}

		if not os.path.isdir(pin_dir):
			os.makedirs(os.path.dirname(self.pin_path))
		if os.path.isfile(self.pin_path):
			with open(self.pin_path) as jsonfile:
				self.pins = json.load(jsonfile)

	def persist_pins(self):
		with open(self.pin_path, 'w') as outfile:
			json.dump(self.pins, outfile, indent=4, sort_keys=True)

	async def add_pin(self, ctx: Context, pin_obj):
		self.pins = {**self.pins, **pin_obj}
		self.logger.debug(f'current pins: {self.pins}')
		await ctx.send(f'✅ Pin saved: {list(pin_obj.keys())[0]}')

	@commands.command(name='pin')
	async def pin(self, ctx: Context, pin_name=None, *, pin_content=None):
		self.logger.info("command called: {}".format(ctx.command))
		if pin_name is None:
			# send usage
			self.logger.debug("empty pin, sending usage")
			todo(self.logger, "send usage")
		elif pin_content is None:
			# find pin with pin_name
			self.logger.debug(f"empty content, looking for pin with name {pin_name}")
			if pin_name in self.pins:
				await ctx.send(self.pins[pin_name])
			else:
				await ctx.send("mivan")
		else:
			pin_obj = {pin_name: pin_content}
			self.logger.debug(f'pinning {pin_name} with content: {pin_content}')
			await self.add_pin(ctx, pin_obj)
			self.persist_pins()

	@commands.command(name='pins')
	async def list_pins(self, ctx: Context, arg=None):
		if arg is not None and arg == "dump":
			await ctx.send(file=discord.File(self.pin_path, 'pins.json'))
		else:
			await ctx.send(f'```{", ".join([pin for pin in self.pins])}```')


async def setup(bot: Bot):
	await bot.add_cog(PinnerCog(bot))
