#!/usr/bin/env python

import unittest
from lib.Server import Server 

class ServerTest(unittest.TestCase):


	def test_server_getname(self):
		server = Server('aws-devbox-root')
		self.assertEqual(server.getName(), 'aws-devbox-root')

	def test_server_getOSType(self):
		server = Server('aws-devbox-root')
		self.assertEqual(server.getOSType(), 'linux')

		#server = Server('testHPUX')
		#self.assertEqual(server.getOSType(), 'hp-ux')

		#server = Server('testAIX')
		#self.assertEqual(server.getOSType(), 'aix')

		#server = Server('testSolaris')
		#self.assertEqual(server.getOSType(), 'solaris')

if __name__ == '__main__':
	unittest.main()

