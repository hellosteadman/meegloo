#!/usr/bin/env python
# encoding: utf-8

from django.db import models
from django.contrib.contenttypes import generic
from django.conf import settings

class ShortLink(models.Model):
	shortcode = models.CharField(max_length = 6, unique = True)
	content_type = models.ForeignKey('contenttypes.ContentType', related_name = 'shortlinks')
	object_id = models.PositiveIntegerField()
	content_object = generic.GenericForeignKey()
	network = models.ForeignKey('networks.Network', related_name = 'shortlinks')
	author = models.ForeignKey('auth.User', related_name = 'shortlinks')
	
	def __unicode__(self):
		return 'http://%s/%s' % (
			getattr(settings, 'URL_SHORTENING_DOMAIN', 'example.com'),
			self.shortcode
		)
		
	def get_redirect_url(self):
		return 'http://%s.%s%s' % (
			self.author.username, self.network.domain,
			self.content_object.get_absolute_url()
		)
	
	def save(self, *args, **kwargs):
		if not self.shortcode:
			import random, string
			
			shortcode = ''.join(random.sample(string.digits + string.letters, 6))
			while ShortLink.objects.filter(shortcode = shortcode).count() > 0:
				shortcode = ''.join(random.sample(string.digits + string.letters, 6))
			
			self.shortcode = shortcode
		
		super(ShortLink, self).save(*args, **kwargs)