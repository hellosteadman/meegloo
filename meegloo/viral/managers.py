#!/usr/bin/env python
# encoding: utf-8

from django.db import models

class CompetitionManager(models.Manager):
	def get_query_set(self):
		return self.model.QuerySet(self.model)
	
	def active(self):
		return self.get_query_set().active()
	
	def summary(self):
		return self.get_query_set().summary()

class EntrantManager(models.Manager):
	def get_query_set(self):
		return self.model.QuerySet(self.model)
	
	def active(self):
		return self.get_query_set().active()
	
	def eligible(self):
		return self.get_query_set().eligible()
	
	def summary(self):
		return self.get_query_set().summary()
		
	def leaderboard(self):
		return self.get_query_set().leaderboard()