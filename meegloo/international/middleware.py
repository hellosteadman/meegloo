#!/usr/bin/env python
# encoding: utf-8

class InternationalMiddleware(object):
	def process_request(self, request):
		from django.conf import settings
		from meegloo.international.models import Country
		
		try:
			from django.contrib.gis.utils import GeoIP
		except ImportError:
			request.country = Country.objects.get(
				pk = getattr(settings, 'COUNTRY_ID')
			)
			
			return
		
		g = GeoIP()
		ip = request.META.get('HTTP_X_FORWARDED_FOR',
			request.META.get('REMOTE_IP', request.META.get('REMOTE_ADDR'))
		)
		
		if ip != '127.0.0.1':
			d = g.country(ip)
			code = d['country_code']
			request.country = Country.objects.get(code = code)
		else:
			pk = getattr(settings, 'COUNTRY_ID')
			request.country = Country.objects.get(pk = pk)