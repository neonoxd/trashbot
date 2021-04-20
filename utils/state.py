import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

module_logger = logging.getLogger('trashbot.State')


@dataclass
class ChannelState:
	id: int
	last_messages: List[int] = field(default_factory=list)

	def add_msg(self, message):
		if len(self.last_messages) == 3:
			del self.last_messages[0]
			self.last_messages.append(hash(message.content))
		else:
			self.last_messages.append(hash(message.content))

	def shall_i(self):
		return self.last_messages[1:] == self.last_messages[:-1] and len(self.last_messages) == 3


@dataclass
class GuildState:
	id: int
	last_slur_dt: datetime = datetime.now()
	channels: List[ChannelState] = field(default_factory=list)
	tension: int = 0
	bee_initialized = False
	bee_active: bool = False
	bee_page: int = 0
	peter_alert: bool = False
	ghost_state: int = 0
	ghost_alerted_today = False

	def get_channel_state_by_id(self, channel_id):
		return next((channel_state for channel_state in self.channels if channel_state.id == channel_id), None)

	def track_channel(self, channel_id):
		module_logger.debug(f"tracking channel: {channel_id}")
		self.channels.append(ChannelState(channel_id))

	def increment_ghost(self):
		self.ghost_state = self.ghost_state + 1 if self.ghost_state < sys.maxsize else 0


@dataclass
class BotState:
	guilds: List[GuildState] = field(default_factory=list)

	def get_guild_state_by_id(self, guild_id):
		return next((guild_state for guild_state in self.guilds if guild_state.id == guild_id), None)

	def track_guild(self, guild_id):
		module_logger.debug(f"tracking guild: {guild_id}")
		self.guilds.append(GuildState(guild_id))


@dataclass
class BotConfig:
	ffmpeg_path: str
	sounds_path: str
	ph_token: str
	sz_id: int
	p_id: int
	slurs: List[str] = field(default_factory=list)
	statuses: List[str] = field(default_factory=list)
	t_states: List[str] = field(default_factory=list)
	ghost_ids: List[int] = field(default_factory=list)
