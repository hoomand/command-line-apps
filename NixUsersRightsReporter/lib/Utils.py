#!/usr/bin/env python
import subprocess
import platform

class Utils(object):

	@staticmethod
	def run(serverName, userName, command):
		# It's best to split given commands by space, even if it's one command with a switch,
		# like 'uname -a', Popen is so picky of its given commands; it likes lists much more than strings
		inputCommands = command.split()
		cmd = []

		if (platform.node().lower() == serverName.lower()):
			# If the serverName provided is the same as the server currently this code is 
			# executed on, we no longer need to SSH to it, we can simply use 'sudo' to run
			# privileged commands
			cmd += ['sudo']
		else:
			SSH_COMMAND = [
				'ssh',
				'-o BatchMode=yes',
				'-o ConnectTimeout=30',
				'-o PasswordAuthentication=no',
				'-o KbdInteractiveAuthentication=no',
				'-o StrictHostKeyChecking=no'
				]

			cmd += SSH_COMMAND
			if userName:
				cmd.append("{0}@{1}".format(userName, serverName))
			else:
				cmd.append("{0}".format(userName))

		cmd += inputCommands

		proc = subprocess.Popen(cmd,stdout=subprocess.PIPE)

		return proc.communicate()[0].strip()
