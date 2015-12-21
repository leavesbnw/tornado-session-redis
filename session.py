#/usr/bin/python
# coding: utf-8

import uuid
import hmac
import ujson
import hashlib
import redis

class Session(dict):
	def __init__(self, session_manager, request_handler):

		self.session_manager = session_manager
		self.request_handler = request_handler
		self.session_id = session_manager.getid(request_handler)
	
	def save(self):
		self.session_manager.set(self,self.request_handler)


class SessionManager(object):
	def __init__(self, secret, store_options, session_timeout):
		self.secret = secret
		self.session_timeout = session_timeout
		try:
			if store_options['redis_pass']:
				self.redis = redis.StrictRedis(host=store_options['redis_host'], port=store_options['redis_port'], password=store_options['redis_pass'])
			else:
				self.redis = redis.StrictRedis(host=store_options['redis_host'], port=store_options['redis_port'])
		except Exception as e:
			print e 
			

	def getid(self,request_handler = None):
		if (request_handler == None):
			session_id = None
		else:
			session_id = request_handler.get_secure_cookie("SID")

		if session_id == None:
			session_id = self._generate_id()
		elif not self.redis.exists(session_id):
			session_id = self._generate_id()
		return session_id
	
	def set(self, session,request_handler):
		request_handler.set_secure_cookie("SID", session.session_id)

		session_data = ujson.dumps(dict(session.items()))

		self.redis.setex(session.session_id, self.session_timeout, session_data)


	def _generate_id(self):
		new_id = hashlib.sha256(self.secret + str(uuid.uuid4()))
		return new_id.hexdigest()


class InvalidSessionException(Exception):
	pass

