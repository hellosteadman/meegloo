#!/usr/bin/env python
# encoding: utf-8

from django.conf import settings
from django.template.loader import select_template

def current_site(request):
	template = select_template(
		(
			'%s/base.html' % request.network.domain,
			'meegloo.com/base.html'
		)
	)
	
	return {
		'API_KEYS': getattr(settings, 'API_KEYS', {}),
		'popup': 'popup' in request.GET,
		'base_template': template,
		'LOCAL': hasattr(settings, 'DOMAIN'),
		'OAUTH_CONSUMERS': getattr(settings, 'OAUTH_CREDENTIALS', {})
	}