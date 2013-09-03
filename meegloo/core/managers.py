#!/usr/bin/env python
# encoding: utf-8

from django.db.models import Manager

class OAuthTokenManager(Manager):
	def get_query_set(self):
		return self.model.QuerySet(self.model)
	
	def with_usernames(self):
		return self.get_query_set().with_usernames()