import logging
from typing import Optional
import discord
from utils.state import TrashBot
from discord.ext import commands
from discord import Attachment, Interaction, app_commands

module_logger = logging.getLogger('trashbot.EventerCog')

class EventerCog(commands.Cog):
    def __init__(self, bot: TrashBot):
            self.bot = bot
            self.logger = module_logger
    
    @app_commands.command(name="add-event", description="Post an event with a thread")
    @app_commands.describe(
        event_name="The name of the event & Date",
        event_link="A link to the event (site, invite, etc.)",
        event_banner="An optional promo image for the event"
    )
    async def slash_add_event(self, interaction: Interaction, event_name: str, event_link: str, event_banner: Optional[Attachment] = None):
        await interaction.response.send_message("sec", ephemeral=True, delete_after=5)
        
        content = f"📢 **{event_name}**"
        if event_banner and event_banner.content_type and event_banner.content_type.startswith("image/"):
            msg = await interaction.channel.send(
                content=content,
                file=await event_banner.to_file()
            )
        else:
            msg = await interaction.channel.send(content=content)
            
        thread = await msg.create_thread(
            name=f"{event_name}",
            auto_archive_duration=60
        )
        
        await thread.send(f"🔗 Event link: {event_link}")

async def setup(bot: TrashBot):
	await bot.add_cog(EventerCog(bot))