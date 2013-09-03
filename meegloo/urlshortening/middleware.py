#!/usr/bin/env python
# encoding: utf-8

from django.conf import settings
from django.http import HttpResponseRedirect
from meegloo.urlshortening.models import ShortLink
import re

URL_SHORTENER_REGEX = re.compile(r'^/(?P<key>\w{6})/?$')

class URLShorteningMiddleware(object):
	def process_request(self, request):
		host = request.META.get('HTTP_HOST', 'meegloo.com')
		if host == 'localhost:8000' or host.endswith('.local:8000'):
			host = getattr(settings, 'DOMAIN')
		
		if host.startswith('www.'):
			host = host[4:]
		
		if host == getattr(settings, 'URL_SHORTENING_DOMAIN'):
			match = URL_SHORTENER_REGEX.match(request.path)
			
			if match:
				shortcode = match.groups()[0]
				
				try:
					shortlink = ShortLink.objects.get(shortcode = shortcode)
					if shortlink.content_object:
						return HttpResponseRedirect(
							shortlink.get_redirect_url()
						)
					else:
						shortlink.delete()
						return HttpResponseRedirect('http://meegloo.com/')
				except ShortLink.DoesNotExist:
					return HttpResponseRedirect('http://meegloo.com/')
			else:
				return HttpResponseRedirect('http://meegloo.com/')