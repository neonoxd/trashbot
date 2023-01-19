import os
import random
import string

import discord
import matplotlib.font_manager as fontman


def todo(logger, msg):
	logger.warn(f'TODO: {msg}')


def has_link(text):
	import re
	# findall() has been used
	# with valid conditions for urls in string
	regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
	url = re.findall(regex, text)
	return [x[0] for x in url]


def create_alphanumeric_string(length):
	return ''.join(random.sample(string.ascii_letters + string.digits, length))


def replace_str_index(text, index=0, replacement=''):
	return '%s%s%s' % (text[:index], replacement, text[index + 1:])


def get_user_nick_or_name(member):
	return member.nick if member.nick is not None else member.name


def find_member_by_id(guild, member_id):
	for member in guild.members:
		if member.id == int(member_id):
			return member


def find_font_file(query):
	matches = list(filter(lambda path: query in os.path.basename(path), fontman.findSystemFonts()))
	return matches


def get_resource_name_or_user_override(res_path):
	usrp = f"usr/{res_path}"
	resp = f"resources/{res_path}"
	return usrp if os.path.isfile(usrp) else resp
