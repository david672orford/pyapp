#! /usr/bin/python
# pyapp/urllib3_cookies.py
# Last modified: 8 January 2015

import urlparse

# Wrap a URL so that it looks enough like a urllib2.Request object
# that cookielib will accept it.
class WrapRequest(object):
	def __init__(self, url):
		self.url = url
		self.url_parsed = urlparse.urlparse(url)
		self.headers = {}
	def get_full_url(self):
		return self.url
	def get_host(self):
		return self.url_parsed.netloc	# contrary to urllib2 docs
	def get_type(self):
		return self.url_parsed.scheme
	def is_unverifiable(self):
		return False
	def get_origin_req_host(self):
		return self.url_parsed.netloc
	def has_header(self, header):
		#print "has_header:", header
		return header in self.headers
	def get_header(self, name, default=None):
		#print "get_header:", name
		return self.headers.get(name, default)
	def add_unredirected_header(self, name, value):
		#print "add header:", name, value
		self.headers[name] = value

# Wrap httplib.Response so that it looks enough like a
# urllib2.Response that cookielib will accept it.
class WrapResponse(object):
	def __init__(self, response):
		#self._info = WrapInfo(response._original_response.msg)
		self._info = response._original_response.msg
	def info(self):
		return self._info

#class WrapInfo(object):
#	def __init__(self, msg):
#		self.msg = msg
#	def getheaders(self, name):
#		print "getheaders:", name
#		matches = self.msg.getheaders(name)
#		print " matches:"
#		for match in matches:
#			print "  %s" % match
#		return matches

# Test
if __name__ == "__main__":
	import urllib3
	import cookielib

	http = urllib3.ProxyManager("http://mouse.trincoll.edu:8080/")
	cookiejar = cookielib.CookieJar()
	
	def request(method, url):
		print "==================================================="
		wrapped_request = WrapRequest(url)
		cookiejar.add_cookie_header(wrapped_request)
		print "sending..."
		r = http.request(method, url, headers=wrapped_request.headers)
		cookiejar.extract_cookies(WrapResponse(r), wrapped_request)
		return r
	
	r = request('GET', 'http://wp.superpages.com')
	print r.status
	print r.headers
	print
	
	r = request('GET', 'http://wp.superpages.com')
	print r.status
	print r.headers
	print
	
