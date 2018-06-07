#!/usr/bin/env python

from lib.Utils import Utils
from lib.Server import Server
from optparse import OptionParser
import sys,os,csv

def createParser():
	parser = OptionParser(usage="%prog [options] -f servers_list_file")
	parser.add_option("-f","--file",dest="serversListFile",metavar="FILE",
			help="servers list file, in format of Application,ServerName (mandatory)")
	parser.add_option("-o", "--output-directory", dest="outputDirectory", default = ".", metavar="FILE",
			help="output directory where output files will be generated. There will be one file per application")
	parser.add_option("-v", action="store_true", dest="verbose",
			help="If -v is set, the output is also displayed on the screen. Without using -v, you will only get the output files")
	return parser

def parseCSV(inputFile):
	file = open(inputFile)
	reader = csv.reader(file)

	output = {}
	for line in reader:
		if line[0] not in output:
			output[line[0]] = []
		output[line[0]].append(line[1])

	return output

def printTitle(title, seperator=False):
	print

	if seperator:
		print "==========================================="

	print title

	if seperator:
		print "==========================================="

	print

if __name__ == '__main__':

	parser = createParser()
	(options,args) = parser.parse_args()
	if(not os.path.isfile(options.serversListFile)):
		parser.print_help()
		sys.exit(1)

	if (options.outputDirectory and not os.path.isdir(options.outputDirectory)):
		parser.print_help()
		sys.exit(1)

	outputDirectory = options.outputDirectory
	headers = "Server Name|User Name|Gecos|Locked|Groups|Sudo Rights"

	appServersList = parseCSV(options.serversListFile)
	for appName,serversList in appServersList.iteritems():
		if options.verbose:
			printTitle("Working on application {0}".format(appName), True)

		with open(os.path.join(outputDirectory, "{0}.psv".format(appName)), 'w') as f:
			f.write(headers+ os.linesep)

			for serverName in serversList:
				if options.verbose:
					printTitle("Parsing server {0}".format(serverName))
					print headers

				server = Server(serverName)
				users = server.getUsers()
				for user in users:
					row = "{0}|{1}|{2}|{3}|{4}|{5}".format(
							server.getName(),
							user.name,
							user.gecos,
							user.isLocked,
							" ".join(user.groups),
							";".join(str(v).strip() for v in user.sudoPerms)
							)
					if options.verbose:
						print row
					f.write(row + os.linesep)

