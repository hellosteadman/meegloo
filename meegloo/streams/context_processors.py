#!/usr/bin/env python
# encoding: utf-8

def latest(request):
	from meegloo.streams.models import Stream
	
	def latest_streams():
		return Stream.objects.filter(
			network = request.network
		).public().order_by('-updated')[:10]
	
	return {
		'latest_streams': latest_streams
	}
	
def settings(request):
	from django.conf import settings as site_settings
	
	return {
		'EXTENSIONS': getattr(site_settings, 'FILE_EXTENSIONS', ())
	}