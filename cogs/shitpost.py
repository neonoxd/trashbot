import asyncio
import logging

import discord
from discord import Message, Member
from discord.ext import commands
from discord.ext.commands import Context
from discord import Embed, app_commands
from utils.helpers import get_member_voice_channel

from utils.state import TrashBot

module_logger = logging.getLogger('trashbot.Shitpost')


class ShitpostCog(commands.Cog):
	def __init__(self, bot: TrashBot):
		module_logger.info("initializing Shitpost")
		self.bot = bot
		self.logger = module_logger
		with open('resources/beemovie.txt', 'r', encoding="utf8") as file:
			self.beescript = file.read().split("\n\n  \n")

		@bot.tree.context_menu(name="nyomod fasz!")
		async def nyomod(interaction: discord.Interaction, message: discord.Message):
			await message.reply("nyomod fasz!!")
			await interaction.response.send_message(content="hehe", ephemeral=True, delete_after=1)

		@bot.tree.context_menu(name="????????")
		async def gunyod(interaction: discord.Interaction, message: discord.Message):
			from cogs.impl.shitpost_impl import get_mock_image
			image_types = [".jpg", ".jpeg", ".png"]
			if len(message.attachments) > 0 and any(attachment.filename.lower().endswith(imgtype) for imgtype in image_types for attachment in message.attachments):
				for attachment in message.attachments:
					await attachment.save(attachment.filename)
					mockimg = get_mock_image(attachment.filename)
					await message.reply(file=discord.File(mockimg, 'mock.png'))
					await interaction.response.send_message(content="hehe", ephemeral=True, delete_after=1)

	@commands.command(name='befli', hidden=True)
	async def befli(self, ctx: Context):
		from cogs.impl.shitpost_impl import command_befli
		await command_befli(self, ctx)

	@commands.command(name='friday', hidden=True)
	async def friday(self, ctx: Context):
		from cogs.impl.shitpost_impl import announce_friday_mfs
		await ctx.message.delete()
		await announce_friday_mfs(self.bot)

	@commands.command(name='captcha')
	async def captcha(self, ctx: Context):
		from cogs.impl.shitpost_impl import command_captcha
		await command_captcha(self, ctx)

	@commands.command(name='tenemos')
	async def tenemos(self, ctx: Context):
		from cogs.impl.shitpost_impl import command_tenemos
		await command_tenemos(self, ctx)

	@commands.command(name="gabo")
	async def gabo(self, ctx: Context, *args):
		from cogs.impl.shitpost_impl import command_gabo
		await command_gabo(self, ctx, args)

	@commands.command(name="sanity")
	async def szabo(self, ctx: Context):
		guild = ctx.bot.guilds[0]
		member_id = ctx.bot.globals.goofies["sz"]
		sz_vc = await get_member_voice_channel(member_id, guild)

		await ctx.message.delete()

		if sz_vc and len(sz_vc.members) > 5:
			msg = await ctx.channel.send("**sanity check...**")
			await asyncio.sleep(2)
			await msg.edit(content="**sanity check...** ❌")
			await asyncio.sleep(3)
			await ctx.message.channel.send(file=discord.File("resources/img/insanity.webp"), content="good luck :)")
		else:
			msg = await ctx.channel.send("**sanity check...**")
			await asyncio.sleep(2)
			await msg.edit(content="**sanity check...** ✅")

	@commands.command(name='beemovie')
	async def bmc(self, ctx: Context, *args):
		from cogs.impl.shitpost_impl import command_beemovie
		await command_beemovie(self, ctx, args)

	@commands.command(name='tension')
	async def show_tension(self, ctx: Context):
		from cogs.impl.shitpost_impl import command_tension
		await command_tension(self, ctx)

	@commands.command(name='gba')
	async def gba(self, ctx: Context):
		from cogs.impl.shitpost_impl import command_gba
		await command_gba(self, ctx)

	@commands.command(name='cz')
	async def cege(self, ctx: Context):
		from cogs.impl.shitpost_impl import command_cz
		await command_cz(self, ctx)

	@app_commands.command(name="cz", description="cegenyit atkereszteli")
	async def cege_new(self, interaction: discord.Interaction):
		from cogs.impl.shitpost_impl import command_cz_new
		await command_cz_new(self, interaction)

	@commands.Cog.listener()
	async def on_voice_state_update(self, member: Member, before, after):
		from cogs.impl.shitpost_impl import event_voice_state_update
		await event_voice_state_update(self, member, before, after)

	@commands.Cog.listener()
	async def on_message(self, message: Message):
		from cogs.impl.shitpost_impl import event_message
		await event_message(self.bot, message)


async def setup(bot: TrashBot):
	await bot.add_cog(ShitpostCog(bot))
