#!/usr/bin/env python
# encoding: utf-8

from django.http import HttpResponseBadRequest
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from piston.handler import BaseHandler
from meegloo.networks.models import Network
from meegloo.api.helpers import format_errors

class NetworkHandler(BaseHandler):
	model = Network
	exclude = ('_state',)
	allowed_methods = ('GET',)
	
	"""
	This interface allows for listing of Meegloo networks.
	"""
	
	def read(self, request, id = None):
		"""
		Returns a list of networks, or a specific stream identified by ''slug''.
		"""
		
		if id:
			result = get_object_or_404(Network, parent = request.network.parent, pk = id)
			return {
				'id': result.pk,
				'name': result.name,
				'domain': result.domain,
				'description': result.description,
				'featured': result.featured,
				'icon': '%d.png' % result.pk
			}
		else:
			result = super(NetworkHandler, self).read(request).filter(
				parent = request.network.parent
			).exclude(
				domain__iexact = request.network.parent.domain
			)
			
			if request.GET.get('lat') and request.GET.get('long'):
				try:
					result = result.near(
						float(request.GET.get('lat')),
						float(request.GET.get('long'))
					)
				except ValueError:
					return HttpResponseBadRequest('lat and/or long values invalid')
				
				values = result.values(
					'id', 'name', 'domain', 'proximity', 'featured'
				)
			else:
				values = result.filter(featured = True).values(
					'id', 'name', 'domain', 'featured'
				)
			
			return [
				{
					'id': v['id'],
					'name': v['name'],
					'domain': v['domain'],
					'featured': v['featured'],
					'icon': '%d.png' % v['id']
				} for v in values
			]