#!/usr/bin/env python

class User(object):

	def __init__(self, userID, userName, gecos, isLocked, groups, sudoPerms = ''):
		self.id = userID
		self.name = userName
		self.gecos = gecos
		self.isLocked = isLocked
		self.groups = groups
		self.sudoPerms = sudoPerms
