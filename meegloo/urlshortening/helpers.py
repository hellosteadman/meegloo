#!/usr/bin/env python
# encoding: utf-8

def shorten(obj, network, author):
	from meegloo.urlshortening.models import ShortLink
	from django.contrib.contenttypes.models import ContentType
	
	shortcode, created = ShortLink.objects.get_or_create(
		content_type = ContentType.objects.get_for_model(obj),
		object_id = obj.pk,
		network = network,
		author = author
	)
	
	return unicode(shortcode)