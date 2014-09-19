# pyapp/save.py
# Last modified: 12 September 2014

import os

class SaveOpen(object):
	def __init__(self, filename, backup=False):
		self.filename = filename
		self.backup = backup

		# MS-DOS naming scheme
		#(base, ext) = os.path.splitext(self.filename)
		#self.tempname = "%s.tmp" % base
		#self.backname = "%s.bak" % base

		# Unix naming scheme
		self.tempname = "%s.tmp" % self.filename
		self.backname = "%s~" % self.filename

		self.fh = open(self.tempname, 'wb')

	def write(self, data):
		self.fh.write(data)

	def close(self):
		self.fh.close()
		if os.path.exists(self.filename):
			if self.backup:
				if os.path.exists(self.backname):
					os.remove(self.backname)
				os.rename(self.filename, self.backname)
			else:
				os.unlink(self.filename)
		os.rename(self.tempname, self.filename)

