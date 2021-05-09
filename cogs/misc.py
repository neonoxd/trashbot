import logging
import random

import aiohttp
from discord.ext import commands

module_logger = logging.getLogger('trashbot.MiscCog')


class MiscCog(commands.Cog):
	def __init__(self, bot):
		module_logger.info("initializing MiscCog")
		self.bot = bot
		self.logger = module_logger

	@commands.command(name="ki", hidden=True)
	async def who(self, ctx, *args):
		guild_state = self.bot.state.get_guild_state_by_id(ctx.message.guild.id)
		if self.bot.user.mentioned_in(ctx.message):
			question = " ".join(args).replace("?","").strip()
			if question in ["", "joinolt", "van itt", "jött fel"]:
				last_joined = guild_state.last_vc_joined
				if last_joined is not None:
					await ctx.send(f"{random.choice(['talán én...de az is lehet hogy ő', 'ez a köcsög', 'ö', 'ha valaki akk ö'])}: {last_joined}")
				else:
					await ctx.send("senki...")
			elif question in ["volt az", "lépett ki", "lépett le", "dczett", "disconnectelt"]:
				last_left = guild_state.last_vc_left
				if last_left is not None:
					await ctx.send(f"{random.choice(['ez a köcsög', 'ö', 'ha valaki akk ö'])} lépett le: {last_left}")
				else:
					await ctx.send("senki...")

	@commands.command(name='say', aliases=['mondd'])
	async def say(self, ctx, *args):
		self.logger.info("command called: {}".format(ctx.command))
		await ctx.message.delete()
		await ctx.send(' '.join(args))

	@commands.command(name='impostor', hidden=True)
	async def impost(self, ctx, *args):
		await ctx.message.delete()
		if len(args) > 0:
			impostor = args[0]
		else:
			impostor = random.choice(ctx.message.channel.members).mention
		tmpl = f""".      　。　　　　•　    　ﾟ　　。
　　.　　　.　　　  　　.　　　　　。　　   。　.
 　.　　      。　        ඞ   。　    .    •
   •        {impostor} was the impostor.　 。　.
　 　　。　　 　　　　ﾟ　　　.　    　　　.
,　　　　.　 .　　       ."""
		await ctx.send(tmpl)

	@commands.command(name="kot")
	async def kot(self, ctx):
		async with aiohttp.ClientSession() as session:
			async with session.get('http://aws.random.cat/meow') as r:
				if r.status == 200:
					js = await r.json()
					await ctx.send(js['file'])


def setup(bot):
	bot.add_cog(MiscCog(bot))
