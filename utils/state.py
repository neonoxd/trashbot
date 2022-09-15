import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List
from discord import Member, VoiceChannel

module_logger = logging.getLogger('trashbot.State')


@dataclass
class UserStats:
	pass


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
class VCEvent:
	event: int
	user: Member
	channel: VoiceChannel
	when: float

@dataclass
class GuildState:
	id: int
	last_slur_dt: datetime = datetime.now()
	channels: List[ChannelState] = field(default_factory=list)
	last_vc_events: List[VCEvent] = field(default_factory=list)
	forced_nicks: dict = field(default_factory=dict)
	tension: int = 0
	bee_initialized = False
	bee_active: bool = False
	bee_page: int = 0
	ghost_state: int = 0
	ghost_alerted_today = False
	last_roll: int = -1

	def force_nick(self, victim: Member, nick: str, invoker: Member):
		module_logger.debug(f"{invoker} forced nick [{nick}] for {victim}")
		self.forced_nicks[victim.id] = {"nick": nick, "invoker": invoker, "when": datetime.now()}

	def clear_nick(self, victim: Member):
		module_logger.debug(f"cleared nick for {victim}")
		self.forced_nicks.pop(victim.id, None)

	def push_last_vc_event(self, event):
		if len(self.last_vc_events) == 10:
			self.last_vc_events.pop(0)
		self.last_vc_events.append(event)

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
	yt_cookie: str
	sz_id: int
	p_id: int
	gba_id: int
	g_id: int
	cz_id: int
	m_id: int
	dzs_id: int
	d_id: int
	l_id: int
	global_timeouts: dict = field(default_factory=dict)
	slurs: List[str] = field(default_factory=list)
	statuses: List[str] = field(default_factory=list)
	t_states: List[str] = field(default_factory=list)
	ghost_ids: List[int] = field(default_factory=list)
	startup_at: datetime = datetime.now()
	queued_hotpots: dict = field(default_factory=dict)

	def add_timeout(self, name: str, expires_at: datetime = None, expiry_td: timedelta = None):
		module_logger.debug(f"adding expire {name}")
		if self.is_expired(name):  # adding new or refreshing
			if expires_at is not None:
				self.global_timeouts[name] = expires_at
				module_logger.debug(f"expire added with param expires_at={expires_at}")
			elif expiry_td is not None:
				self.global_timeouts[name] = datetime.now() + expiry_td
				module_logger.debug(f"expire added with param expiry_td={expiry_td}")
		else:
			module_logger.warning(f"expire already exists with name: {name}")

	def is_expired(self, name: str):
		if (name in self.global_timeouts and datetime.now() >= self.global_timeouts[name]) or name not in self.global_timeouts:
			return True
		else:
			return False
