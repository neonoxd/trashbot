import dataclasses
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

import discord
from discord import Member, VoiceChannel
from discord.ext import commands

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
	channels: List[ChannelState] = field(default_factory=list)
	last_vc_events: List[VCEvent] = field(default_factory=list)
	forced_nicks: dict = field(default_factory=dict)
	last_slur_dt: datetime = datetime.now()
	tension: int = 0
	bee_initialized = False
	bee_active: bool = False
	bee_page: int = 0
	ghost_state: int = 0
	ghost_alerted_today = False
	last_roll: int = -1
	last_shaolin_appearance: datetime = datetime.fromtimestamp(0)

	def serialize(self):
		js = json.dumps(self, cls=EnhancedJSONEncoder)
		module_logger.info(js)

	def save_state(self):
		module_logger.info("saving state...")
		state = {
			"last_slur_dt": self.last_slur_dt.isoformat(),
			"tension": self.tension,
			"ghost_state": self.ghost_state,
			"ghost_alerted_today": self.ghost_alerted_today,
			"last_shaolin_appearance": self.last_shaolin_appearance.isoformat(),
		}
		state_json = json.dumps(state)
		module_logger.debug(state_json)
		with open(f"usr/state/guild_{self.id}.json", "w") as f:
			f.write(state_json)
		return state_json

	def load_state(self):
		module_logger.info("loading state...")
		state_file = f"usr/state/guild_{self.id}.json"
		if not os.path.isfile(state_file):
			module_logger.warning(f"no state found for guild: {self.id}")
			return
		with open(state_file, "r") as f:
			saved_state = json.load(f)
			module_logger.debug(saved_state)
			self.last_slur_dt = datetime.fromisoformat(saved_state["last_slur_dt"])
			self.tension = saved_state["tension"]
			self.ghost_state = saved_state["ghost_state"]
			self.ghost_alerted_today = saved_state["ghost_alerted_today"]
			self.last_shaolin_appearance = datetime.fromisoformat(saved_state["last_shaolin_appearance"])
		os.remove(state_file)

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
	quotecfg: dict = field(default_factory=dict)
	quotecontent: dict = field(default_factory=dict)
	motd: discord.Embed = None

	def get_guild_state_by_id(self, guild_id) -> GuildState:
		return next((guild_state for guild_state in self.guilds if guild_state.id == guild_id), None)

	def track_guild(self, guild_id):
		module_logger.debug(f"tracking guild: {guild_id}")
		gs = GuildState(guild_id)
		gs.load_state()
		self.guilds.append(gs)


@dataclass
class BotConfig:
	ffmpeg_path: str
	sounds_path: str
	ph_token: str
	yt_cookie: str
	global_timeouts: dict = field(default_factory=dict)
	slurs: List[str] = field(default_factory=list)
	statuses: List[str] = field(default_factory=list)
	t_states: List[str] = field(default_factory=list)
	ghost_ids: List[int] = field(default_factory=list)
	startup_at: datetime = datetime.now()
	queued_hotpots: dict = field(default_factory=dict)
	verinfo: dict = field(default_factory=dict)
	goofies: dict = field(default_factory=dict)
	greetings: dict = field(default_factory=dict)

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


class EnhancedJSONEncoder(json.JSONEncoder):
	def default(self, o):
		if isinstance(o, datetime):
			return o.isoformat()
		if isinstance(o, VCEvent) or isinstance(o, ChannelState):
			return None
		if dataclasses.is_dataclass(o):
			return dataclasses.asdict(o, dict_factory=lambda x: {k: v for (k, v) in x if v is not None and k not in ["channels", "last_vc_events"]})
		return super().default(o)


class TrashBot(commands.Bot):
	state: BotState
	globals: BotConfig
	logger: logging.Logger

	def log(self, message: str, name: str, level: int = logging.INFO, **kwargs) -> None:
			self.logger.name = name
			self.logger.log(level = level, msg = message, **kwargs)
