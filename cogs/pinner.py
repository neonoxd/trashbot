import json
import logging
import os

import discord
from discord.ext import commands
from discord.ext.commands import Context

from utils.helpers import todo
from utils.state import TrashBot

module_logger = logging.getLogger('trashbot.PinnerCog')


class PinModal(discord.ui.Modal, title='Saving Pin'):
	name = discord.ui.TextInput(label='Name')

	def __init__(self, cog, message: discord.Message, timeout=180):
		super().__init__(timeout=timeout)
		self.cog = cog
		self.message = message
		module_logger.debug(message)

	async def on_submit(self, interaction: discord.Interaction):
		if len(self.message.attachments) > 1:
			pin_content = [att.url for att in self.message.attachments]
		elif len(self.message.attachments) > 0:
			pin_content = self.message.attachments[0].url
		else:
			pin_content = self.message.content

		pin_obj = {str(self.name): pin_content}
		self.cog.logger.debug(f'pinning {self.name} with content: {self.message.content}')
		await self.cog.add_pin2(interaction, pin_obj, self.message)
		self.cog.persist_pins()
		await interaction.response.defer()


class PinnerCog(commands.Cog):
	def __init__(self, bot: TrashBot):
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

		@bot.tree.context_menu(name="tűzzed báttya!")
		async def pin(interaction: discord.Interaction, message: discord.Message):
			await interaction.response.send_modal(PinModal(self, message))

	def persist_pins(self):
		with open(self.pin_path, 'w') as outfile:
			json.dump(self.pins, outfile, indent=4, sort_keys=True)

	async def add_pin(self, ctx: Context, pin_obj):
		self.pins = {**self.pins, **pin_obj}
		await ctx.send(f'✅ Pin saved: {list(pin_obj.keys())[0]}')

	async def add_pin2(self, interaction: discord.Interaction, pin_obj, message: discord.Message):
		self.pins = {**self.pins, **pin_obj}
		who = interaction.user.nick if interaction.user.nick is not None else interaction.user.name
		await message.reply(f'megjegyeztem {who}...{list(pin_obj.keys())[0]} 📌')

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


async def setup(bot: TrashBot):
	await bot.add_cog(PinnerCog(bot))
