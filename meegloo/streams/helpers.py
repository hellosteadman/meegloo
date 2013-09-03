#!/usr/bin/env python
# encoding: utf-8

import re

DOMAIN_MATCH = re.compile(r'^(?P<domain>[a-zA-z0-9\.]+)(?P<port>\:\d+)?$')

def upload_post_media(instance, filename):
	from uuid import uuid4
	from datetime import datetime
	from os import path
	
	date = instance.post.posted or datetime.now()
	return path.join(
		instance.post.kind,
		instance.post.stream.part_of.slug,
		unicode(date.year),
		unicode(date.month).zfill(2),
		unicode(uuid4()) + path.splitext(filename)[-1]
	)
	
def reverse_geocode(latitude, longitude):
	from django.utils import simplejson
	from urllib import urlopen
	
	url = 'http://api.geonames.org/findNearbyPlaceNameJSON?lat=%s&lng=%s&username=meegloo' % (
		latitude, longitude
	)
	
	request = urlopen(url)
	
	try:
		json = simplejson.load(request)
	finally:
		request.close()
	
	names = json.get('geonames', [])
	if len(names) > 0:
		return '%s, %s' % (
			names[0]['name'],
			names[0]['countryName']
		)
	
	return None

def clean_domain(value):
	domain = value.lower().strip()
	
	if domain.startswith('www.'):
		domain = domain[4:]
	
	if domain.startswith('.'):
		domain = domain[1:]
	
	if domain.endswith('.'):
		domain = domain[:-1]
	
	if domain.endswith(','):
		domain = domain[:-1]
	
	if domain.endswith(';'):
		domain = domain[:-1]
	
	match = DOMAIN_MATCH.match(domain)
	if match:
		return match.groupdict()['domain']
	else:
		raise Exception('Not a valid domain')

def post_save(sender, instance, created, **kwargs):
	if not created:
		return
	
	posts = type(instance).objects.public().filter(
		stream__part_of = instance.stream.part_of
	).exclude(pk = instance.pk).count()
	
	if posts == 0 and instance.stream.part_of.get_twitter_tags(instance.author).count() > 0:
		instance.stream.part_of.update_twitter(instance.author)