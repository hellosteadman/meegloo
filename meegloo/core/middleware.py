#!/usr/bin/env python
# encoding: utf-8

from django.http import HttpResponseRedirect, Http404
from django.conf import settings

class AdminMiddleware(object):
	def process_request(self, request):
		if request.path.startswith('/admin/'):
			if hasattr(request, 'network') and request.network:
				if getattr(settings, 'TESTING', False):
					return
				
				if hasattr(request, 'profile') and request.profile:
					return HttpResponseRedirect('http://%s/admin/' % request.network.parent.domain)
				
				if request.network.domain != request.network.parent.domain:
					return HttpResponseRedirect('http://%s/admin/' % request.network.parent.domain)
			
			ip = request.META.get('HTTP_X_FORWARDED_FOR',
				request.META.get('REMOTE_IP', request.META.get('REMOTE_ADDR'))
			)
			
			if not ip in getattr(settings, 'ADMIN_IPS', []):
				raise Http404()