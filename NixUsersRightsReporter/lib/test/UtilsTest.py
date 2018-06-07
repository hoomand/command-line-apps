#!/usr/bin/env python

import unittest
from lib.Utils import Utils 

class UtilsTest(unittest.TestCase):


	def test_ssh(self):
		output = Utils.run('aws-devbox-root', 'root', 'uname -a')
		self.assertEqual(output, 'Linux aws-devbox 4.1.10-17.31.amzn1.x86_64 #1 SMP Sat Oct 24 01:31:37 UTC 2015 x86_64 x86_64 x86_64 GNU/Linux')

if __name__ == '__main__':
	unittest.main()

