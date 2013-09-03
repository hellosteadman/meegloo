#!/usr/bin/env python
# encoding: utf-8

from django.db.models import Manager

class NetworkManager(Manager):
	def get_query_set(self):
		return self.model.QuerySet(self.model)
	
	def public(self):
		return self.get_query_set().public()
	
	def external(self):
		return self.get_query_set().external()
	
	def near(self, latitude, longitude):
		return self.get_query_set().near(latitude, longitude)