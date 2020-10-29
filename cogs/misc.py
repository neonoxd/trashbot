import logging

from discord.ext import commands

module_logger = logging.getLogger('trashbot.MiscCog')


class MiscCog(commands.Cog):
	def __init__(self, bot):
		module_logger.info("initializing MiscCog")
		self.bot = bot
		self.logger = module_logger

	@commands.command(name='say')
	async def say(self, ctx, *args):
		self.logger.info("command called: {}".format(ctx.command))
		await ctx.send(' '.join(args))


def setup(bot):
	bot.add_cog(MiscCog(bot))
