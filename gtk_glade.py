import os
import sys
import gtk
import gettext

class GladeWidget(gtk.VBox):
	def __init__(self, glade_file, top_obj):
		gtk.VBox.__init__(self)

		print "Loading %s..." % glade_file
		glade_file_path = os.path.join(sys.path[0], glade_file)
		self.builder = gtk.Builder()
		self.builder.set_translation_domain(gettext.textdomain())
		self.builder.add_from_file(glade_file_path)

		self.pack_start(self.builder.get_object(top_obj), True, True)
		self.builder.connect_signals(self)

