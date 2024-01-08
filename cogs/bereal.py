import logging
import typing
from datetime import datetime
from typing import List, Optional

import discord
from discord import Thread, Member, TextChannel, Message, app_commands
from discord.ext import commands

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
        if len(self.posts) > 0:
            self.last = await self.find_best_message()
        else:
            self.last = None

        self.posts = []
        self.current_thread = await self.create(channel)

        if self.last is not None:
            await channel.send(f"Arany Komédia tegnapról {self.last.jump_url} {self.last.author.mention}")

    @app_commands.command(name="real-comedy-start")
    @commands.is_owner()
    async def start_comedy(self, interaction: discord.Interaction):
        """ /real-comedy-start """
        await interaction.response.send_message(content="zsa", ephemeral=True, delete_after=1)
        channel: TextChannel = typing.cast(TextChannel, interaction.channel)
        await self.do(channel)

    @app_commands.command(name="real-comedy-gold")
    async def show_last_gold(self, interaction: discord.Interaction):
        """ /real-comedy-gold - show the best from last """
        if self.last is not None:
            best: Message = self.last
            await interaction.response.send_message(content=f"Arany Komédia tegnapról {best.jump_url} {best.author.mention}")
        else:
            await interaction.response.send_message(content="vársz", delete_after=1)

    async def find_best_message(self) -> Message:
        return max(self.posts, key=lambda x: len(x.reactions))

    @staticmethod
    async def create(channel: TextChannel, initiator: Member | None = None) -> Thread:
        module_logger.info(f"BeReal Triggered by {initiator}")
        message = await channel.send(f"⚠️ Komédia™️(BETA) idő ⚠️\n"
                                     f"_**10 perced** van a fonákba elküldeni a legviccesebb vizuális tartalmat_\n"
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
                or type(message.channel) != Thread \
                or self.current_thread is None \
                or message.channel.id != self.current_thread.id \
                or len(message.attachments) == 0 \
                or message.author in [msg.author for msg in self.posts]:
            return
        
        module_logger.info(f"got a new post in {message.channel.name} by {message.author}")
        self.posts.append(message)
        if (message.created_at - self.current_thread.created_at).total_seconds() / 60 >= 10:
            await message.add_reaction("❌")
        else:
            await message.add_reaction("✅")


async def trigger_real_comedy(bot: TrashBot, channel: TextChannel):
    from utils.helpers import schedule_real_comedy
    cog: Optional[BeRealCog] = bot.get_cog('BeRealCog')
    await cog.do(channel)
    bot.loop.create_task(schedule_real_comedy(bot, channel))


async def setup(bot: TrashBot):
    await bot.add_cog(BeRealCog(bot))
