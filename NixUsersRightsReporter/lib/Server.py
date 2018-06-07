#!/usr/bin/env python
import subprocess
import logging
import re
from cStringIO import StringIO
from lib.Sudo import * 
from lib.Utils import Utils
from lib.User import User

class Server(object):

	def __init__(
			self,
			name = 'localhost',
			id = '',
			fqdn = '',
			role = '',
			support_group = '',
			console = '',
			os_type = '',
			os_name = '',
			os_version = '',
			date_created = '',
			user = 'root'
			):
		self.name = name 
		self.id = id
		self.fqdn = fqdn
		self.role = role
		self.support_group = support_group
		self.console = console
		self.os_type = os_type
		self.os_name = os_name
		self.os_version = os_version
		self.date_created = date_created
		self.user = user

		self.applications = []
		self.files = {}
		self._users = []
		self._shadows = []

		self._areFilesRead = False

	def __str__(self):
		attrs = vars(self)
		return ', '.join("%s: %s" % item for item in attrs.items())

	def __eq__(self, other):
		return (
				self.name == other.name and
				self.id == other.id and
				self.fqdn == other.fqdn and
				self.role == other.role and
				self.support_group == other.support_group and
				self.console == other.console and
				self.os_type == other.os_type and
				self.os_name == other.os_name and
				self.os_version == other.os_version
				)
	
	def run(self, command):
		return Utils.run(self.getName(), self.user, command)

	def isRemote(self):
		if (self.name != 'localhost'):
			return True

		return False

	def getName(self):
		return self.name

	def getID(self):
		return self.id

	def getOSType(self):
		if (self.os_type == ''):
			uname = self.run('uname -a')
			uname = str.lower(uname)
			if ('solaris' in uname or 'sunos' in uname):
				self.os_type = 'solaris'
			elif ('linux' in uname):
				self.os_type = 'linux'
			elif ('aix' in uname):
				self.os_type = 'aix'
			elif ('hp-ux' in uname):
				self.os_type = 'hp-ux'

		return self.os_type

	def setApps(self, applications):
		self.applications = applications

	def getMainApp(self):
		if self.applications:
			return self.applications[0]
		else:
			return None

	def getApps(self):
		return self.applications

	# Getting the location of sudo file on the server
	def getSudoersFileLocation(self):
		location = "/etc/sudoers"
		if self.run('if [[ -f /usr/local/etc/sudoers ]]; then echo "yes"; else echo "no"; fi') == "yes":
				location = "/usr/local/etc/sudoers"
		return location


	def _readFiles(self):
		# We only want to read files once for each server instance
		if self._areFilesRead:
			return

		self.files["passwd"] = self.run('egrep -v "^#|^$" /etc/passwd')
		self.files["group"] = self.run('egrep -v "^#|^$" /etc/group')
		self.files["sudoers"] = self.run('egrep -v "^#|^$" {0}'.format(self.getSudoersFileLocation()))
		self.files["shadow"] = ""

		self.getOSType()
		if (self.os_type in ["linux", "solaris"]):
			self.files["shadow"] = self.run('egrep -v "^#|^$" /etc/shadow')
			for line in self.files["shadow"].split("\n"):
				self._shadows.append(line.split(":"))

		self._areFilesRead = True

	def getPasswdFile(self):
		self._readFiles()
		return self.files["passwd"]

	def getGroupFile(self):
		self._readFiles()
		return self.files["group"]

	def getSudoersFile(self):
		self._readFiles()
		return self.files["sudoers"]

	def getShadowFile(self):
		self._readFiles()
		return self.files["shadow"]

	def isUserLocked(self, username):
		self.getOSType()
		self._readFiles()

		if (self.os_type in ['linux', 'solaris']):
			# read shadow file
			try:
				password = [x[1] for x in self._shadows if x[0] == username][0]
				if (password.startswith("!!") or password.startswith("*LK*")):
					return True
			except:
				print "Error: parsing /etc/shadow file for user {0}".format(username)
				return False

		elif (self.os_type == 'aix'):
			# run lsuser -f for that user
			try:
				x = self.run('lsuser -f {0} | grep lock'.format(username))
				userLocked = x.strip().split("=")[1]
				if (userLocked == 'true'):
					return True
			except:
				print "Error: AIX lsuser didn't return as expected"
				return False
		elif (self.os_type == 'hp-ux'):
			# run hp-ux specific command
			try:
				x = self.run('/usr/lbin/getprpw -m alock {0}'.format(username)) 
				userLocked = x.strip().split("=")[1].lower()
				if (userLocked == 'yes'):
					return True
			except:
				print "Error: HP-UX /usr/lbin/getprpw did not return a good value for user {0}".format(username)
				return False

		return False


	def getUsers(self, verbose = False):
		self._users = []
		self._readFiles()

		sudoFileObject = StringIO(self.files["sudoers"])
		sp = SudoersParser()
		sp.parseFile(sudoFileObject)

		# TODO: clean up, use one variable
		for ul in self.files["passwd"].split("\n"):
			username = ""
			username = ul.split(":")[0]
			userID = ul.split(":")[2]
			userGecos = ul.split(":")[4]
			userPrimaryGroupID = ul.split(":")[3]
			userShell = ul.split(":")[6]
			userLocked = self.isUserLocked(username)

			if verbose:
				logging.warning("Working on user {0}".format(username))

			# Get groups
			groups = []
			for gl in self.files["group"].split("\n"):
				groupName = gl.split(":")[0]
				groupID = gl.split(":")[2]
				groupUsers = gl.split(":")[3]
				if  userPrimaryGroupID == groupID or groupUsers.find(username) != -1:
					groups.append(groupName)

			# Get sudo permissions
			userSudoPerms = sp.getCommands(username)
			# TODO: put this in a separate function, to get all OS group privileges in sudoers file
			for group in groups:
				for sudoline in self.files["sudoers"].split("\n"):
					if re.search("^%{0} \S*".format(group), sudoline):
						userSudoPerms.append(sudoline)
			user = User(userID, username, userGecos, userLocked, groups, userSudoPerms)
			self._users.append(user)
		return self._users
