#!/usr/bin/env python
# encoding: utf-8

from django.db import models
from meegloo.networks import NETWORK_PRIVACY_CHOICES, helpers, managers as mans

class SuperNetwork(models.Model):
	name = models.CharField(max_length = 50)
	domain = models.CharField(max_length = 50, unique = True)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ('name',)

class Network(models.Model):
	name = models.CharField(max_length = 50)
	domain = models.CharField(max_length = 50, unique = True)
	privacy = models.IntegerField(choices = NETWORK_PRIVACY_CHOICES, default = 1)
	owner = models.ForeignKey('auth.User', related_name = 'owned_networks')
	managers = models.ManyToManyField('auth.User', related_name = 'managed_networks', blank = True)
	parent = models.ForeignKey('SuperNetwork', related_name = 'children')
	logo = models.ImageField(upload_to = helpers.upload_logo, null = True, blank = True)
	icon = models.ImageField(upload_to = helpers.upload_icon, null = True, blank = True)
	featured = models.BooleanField()
	description = models.TextField(null = True, blank = True)
	latitude = models.CharField(max_length = 30, null = True, blank = True)
	longitude = models.CharField(max_length = 30, null = True, blank = True)
	objects = mans.NetworkManager()
	
	def __unicode__(self):
		return self.name
	
	def get_absolute_url(self):
		return 'http://%s/' % self.domain
	
	def get_profile_url(self, user):
		return 'http://%s.%s' % (user.username, self.domain)
	
	@property
	def is_external(self):
		return self.pk > 1
	
	class QuerySet(models.query.QuerySet):
		def near(self, latitude, longitude):
			sql = """((ACOS(SIN(%(latitude)s * PI() /
			180) * SIN(`%(Network)s`.`latitude` * PI() / 180) + COS(%(latitude)s * PI() / 180) *
			COS(`%(Network)s`.`latitude` * PI() / 180) * COS((%(longitude)s - 
			`%(Network)s`.`longitude`) * PI() / 180)) * 180 / PI()) * 60 * 1.1515)""" % {
				'latitude': latitude,
				'longitude': longitude,
				'Network': Network._meta.db_table,
			}
			
			qs = self.exclude(
				latitude = '',
				longitude = '',
				latitude__isnull = True,
				longitude__isnull = True
			).extra(
				select = {
					'proximity': sql
				}
			).extra(
				where = [
					'%s <= 25' % sql
				]
			).order_by('proximity', '-featured')
			
			return qs
		
		def public(self):
			return self.filter(privacy__gt = 0)
		
		def external(self):
			from django.db.models import F
			
			return self.exclude(
				domain__iexact = F('parent__domain')
			)
	
	class Meta:
		ordering = ('-featured', 'name',)