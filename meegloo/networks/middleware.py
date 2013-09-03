#!/usr/bin/env python
# encoding: utf-8

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from meegloo.networks.models import Network

class NetworkMiddleware(object):
	def process_request(self, request):
		host = request.META.get('HTTP_HOST', 'meegloo.com')
		if host == 'localhost:8000' or host.endswith('.local:8000'):
			host = getattr(settings, 'DOMAIN')
		
		if host.startswith('www.'):
			host = host[4:]
		
		portions = host.lower().split('.')
		if hasattr(request, 'profile') and request.profile:
			portions = portions[1:]
		
		host = '.'.join(portions)
		try:
			request.network = Network.objects.get(domain = host)
			request.profile = None
		except Network.DoesNotExist:
			username = portions.pop(0)
			host = '.'.join(portions)
			
			try:
				request.network = Network.objects.get(domain = host)
				try:
					request.profile = User.objects.get(username = username)
				except User.DoesNotExist:
					return HttpResponseRedirect(
						'http://%s/signup?username=%s' % (host, username)
					)
			except Network.DoesNotExist:
				return HttpResponse('Network not found at domain %s' % request.META['HTTP_HOST'])