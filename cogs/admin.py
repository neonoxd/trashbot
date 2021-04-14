import logging

from discord.ext import commands

module_logger = logging.getLogger('trashbot.AdminCog')


class AdminCog(commands.Cog):
	def __init__(self, bot):
		module_logger.info("initializing AdminCog")
		self.bot = bot
		self.logger = module_logger

	@commands.command(name='phtoken', hidden=True)
	@commands.is_owner()
	async def set_ph_token(self, ctx, *args):
		await ctx.message.delete()
		self.bot.globals.ph_token = args[0]


def setup(bot):
	bot.add_cog(AdminCog(bot))
