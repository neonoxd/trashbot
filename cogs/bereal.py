import logging
from datetime import datetime
from typing import List, Optional

from discord import Thread, Member, TextChannel, Message
from discord.ext import commands
from discord.ext.commands import Context

from utils.state import TrashBot

module_logger = logging.getLogger('trashbot.BeRealCog')


class BeRealCog(commands.Cog):
	def __init__(self, bot: TrashBot):
		module_logger.info("initializing BeRealCog")
		self.bot: TrashBot = bot
		self.logger = module_logger
		self.current_thread: Thread | None = None
		self.posts: List[Message] = []
		self.last: Message | None = None

	async def do(self, channel: TextChannel):
		self.current_thread = await self.create(channel)
		self.posts = []

	@commands.command(name='bereal')
	@commands.guild_only()
	@commands.is_owner()
	async def manual_run(self, ctx: Context):
		await ctx.message.delete()
		await self.do(ctx.channel)

	@commands.command(name='real')
	async def current(self, ctx: Context):
		await ctx.message.delete()
		best: Message = await self.find_best_message()
		await ctx.message.channel.send(f"Arany Komédia {best.jump_url} {best.author.mention}")

	async def find_best_message(self) -> Message:
		return max(self.posts, key=lambda x: len(x.reactions))

	@staticmethod
	async def create(channel: TextChannel, initiator: Member | None = None) -> Thread:
		module_logger.info(f"BeReal Triggered by {initiator}")
		message = await channel.send(f"⚠️ Komédia™️(BETA) idő ⚠️\n"
									 f"_2 perced van a fonákba elküldeni a legviccesebb vizuális tartalmat_\n"
									 f"_Ha késel sajnos meghalsz_")
		thread = await message.create_thread(
			name=f"BR{datetime.today().strftime('%y%m%d')}"
		)
		module_logger.info(f"thread created {thread.name}")
		return thread

	@commands.Cog.listener()
	async def on_message(self, message: Message):
		if message.author == self.bot.user \
				or not message.guild \
				or self.current_thread is None \
				or message.channel.id != self.current_thread.id \
				or len(message.attachments) == 0 \
				or message.author in [msg.author for msg in self.posts]:
			return

		module_logger.info(f"got a new post in {message.channel.name} by {message.author}")

		self.posts.append(message)

		if (message.created_at - self.current_thread.created_at).total_seconds() / 60 > 2:
			await message.add_reaction("❌")
		else:
			await message.add_reaction("✅")


async def trigger_first_real(bot: TrashBot, channel: TextChannel):
	from utils.helpers import sched_real
	cog: Optional[BeRealCog] = bot.get_cog('BeRealCog')
	await cog.do(channel)
	bot.loop.create_task(sched_real(bot, channel))


async def setup(bot: TrashBot):
	await bot.add_cog(BeRealCog(bot))
