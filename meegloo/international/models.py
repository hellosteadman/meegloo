#!/usr/bin/env python
# encoding: utf-8

from django.db import models

class Currency(models.Model):
	code = models.CharField(max_length = 3, unique = True)
	name = models.CharField(max_length = 50)
	symbol = models.CharField(max_length = 5)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ('name',)

class Country(models.Model):
	code = models.CharField(max_length = 2, unique = True)
	name = models.CharField(max_length = 50)
	currency = models.ForeignKey(Currency, related_name = 'countries')
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ('name',)

class TimeZone(models.Model):
	code = models.CharField(max_length = 3, unique = True)
	name = models.CharField(max_length = 50)
	offset_hours = models.IntegerField()
	offset_minutes = models.PositiveIntegerField()
	
	def __unicode__(self):
		if self.offset_hours != 0 or self.offset_minutes > 0:
			if self.offset_hours > 0:
				symbol = '+'
			else:
				symbol = ''
			
			offset = ' %s%02d:%02d' % (symbol, self.offset_hours, self.offset_minutes)
		else:
			offset = ''
		
		return u'%s (%s)%s' % (self.code, self.name, offset)
	
	def now(self):
		from datetime import datetime, timedelta
		
		return datetime.now() + timedelta(
			hours = self.offset_hours,
			minutes = self.offset_minutes
		)
	
	class Meta:
		ordering = ('offset_hours', 'offset_minutes')