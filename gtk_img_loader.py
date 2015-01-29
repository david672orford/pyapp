# pyapp/gtk_img_loader.py
# Copyright 2015, Trinity College
# Last modified: 16 January 2015

import threading
import urllib3
import gobject
import gtk
from collections import OrderedDict

# This is a wrapper for the real object which avoids all of the
# unexplained self references which the real object gets as soon
# as it calls self.start().
class ImgLoader(object):
	def __init__(self, image):
		self.thread = _ImgLoader(image)
	def __del__(self):
		self.thread.shutdown()
	def set_url(self, url):
		self.thread.set_url(url)

# This object runs a thread to download images as load them in into
# a gtk.Image() indicated by the "image" parameter.
class _ImgLoader(threading.Thread):
	def __init__(self, image):
		threading.Thread.__init__(self)
		self.image = image
		self.pool = urllib3.PoolManager()
		self.url = None
		self.syncer = threading.Condition()
		self.ram_cache = OrderedDict()
		self.ram_cache_max = 100			# number of entries
		self.daemon = True

	def shutdown(self):
		print "ImgLoader: shutdown()"
		if self.is_alive():
			with self.syncer:
				self.url = None		# stop signl
				self.syncer.notify()
			self.join()
		print "ImgLoader: thread exited"

	def set_url(self, url):
		print "ImgLoader: Set image url:", url
		with self.syncer:
			self.url = url
			if url in self.ram_cache:
				pixbuf = self.ram_cache.pop(url)
				self.gtk_callback(url, pixbuf)
				self.ram_cache[url] = pixbuf		# put back at top
			else:
				if not self.is_alive():
					self.start()					# start the thread
					self.syncer.wait()				# wait for it to say that it is ready
				self.syncer.notify()

	# Run in separate thread
	def run(self):
		with self.syncer:							# tell parent thread we are ready
			self.syncer.notify()
		while True:
			with self.syncer:						# wait for an URL to load
				self.syncer.wait()
				url = self.url
			if url is None:
				break
			print "ImgLoader: Fetching: %s" % url
			response = self.pool.request("GET", url,
				headers={
					'User-Agent': 'PyApp/20150115',
					'Accept': 'image/jpeg',
					},
				timeout=5,
				)
			print "  Status: %s" % response.status
			print "  Content-Type: %s" % response.headers['content-type']
			print "  Headers:", response.headers
			if response.status == 200:
				loader = gtk.gdk.PixbufLoader()
				loader.write(response.data)
				loader.close()
				pixbuf = loader.get_pixbuf()
				gobject.idle_add(lambda: self.gtk_callback(url, pixbuf))

	def gtk_callback(self, url, pixbuf):
		if url == self.url:		# if still needed
			print "ImgLoader: Displaying %s" % url
			self.image.set_from_pixbuf(pixbuf)
		else:
			print "ImgLoader: no longer needed %s" % url
		with self.syncer:
			if len(self.ram_cache) > self.ram_cache_max: 	# if cache full,
				self.ram_cache.popitem(last=False)			# discard from bottom
			self.ram_cache[url] = pixbuf

if __name__ == "__main__":
	import gobject
	import gtk
	import sys, gc
	gobject.threads_init()
	w = gtk.Window()
	w.show()
	image = gtk.Image()
	w.add(image)
	image.show()
	image_loader = ImgLoader(image)
	image_loader.set_url('http://maps.googleapis.com/maps/api/streetview?size=200x200&location=42.132999,-72.740349')
	print "final refcount:", sys.getrefcount(image_loader)
	gtk.main()


