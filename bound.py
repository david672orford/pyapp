import weakref
import new
class BoundMethodProxy(object):
	def __init__(self, bound_method):
		self.im_self_ref = weakref.ref(bound_method.im_self)
		self.im_func = bound_method.im_func
		self.im_class = bound_method.im_class
	def __call__(self, *args, **kwargs):
		obj = self.im_self_ref()
		if obj is None:
			raise ReferenceError
		return new.instancemethod(self.im_func, obj, self.im_class)(*args, **kwargs)
