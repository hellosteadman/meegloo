#!/usr/bin/env python
# encoding: utf-8

def settings(request):
	from django.conf import settings as django_settings
	
	return {
		'UPLOADIFY_URL': getattr(django_settings, 'UPLOADIFY_URL')
	}