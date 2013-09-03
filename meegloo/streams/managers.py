#!/usr/bin/env python
# encoding: utf-8

from django.db.models import Manager

class StreamManager(Manager):
	def get_query_set(self):
		return self.model.QuerySet(self.model)
	
	def near(self, latitude, longitude):
		return self.get_query_set().near(latitude, longitude)
	
	def public(self):
		return self.get_query_set().public()
		
	def summary(self):
		return self.get_query_set().summary()

class UserStreamManager(Manager):
	def get_query_set(self):
		return self.model.QuerySet(self.model)
	
	def near(self, latitude, longitude):
		return self.get_query_set().near(latitude, longitude)
	
	def live(self):
		return self.get_query_set().live()
	
	def public(self):
		return self.get_query_set().public()
		
	def summary(self):
		return self.get_query_set().summary()

class PostManager(Manager):
	def get_query_set(self):
		return self.model.QuerySet(self.model)
	
	def live(self):
		return self.get_query_set().live()
	
	def public(self):
		return self.get_query_set().public()

class MediaManager(Manager):
	def get_query_set(self):
		return self.model.QuerySet(self.model)
	
	def image(self):
		return self.get_query_set().image()
	
	def flv(self):
		return self.get_query_set().flv()
	
	def mp3(self):
		return self.get_query_set().mp3()
	
	def mp4(self):
		return self.get_query_set().mp4()

class TrendManager(Manager):
	def get_query_set(self):
		return self.model.QuerySet(self.model)
	
	def rebuild(self):
		self.get_query_set().rebuild()