#!/usr/bin/env python
# encoding: utf-8

from meegloo.networks.models import Network

def networks(request):
	if request.user.is_authenticated():
		networks = Network.objects.filter(
			parent = request.network.parent,
			pk__in = request.user.streams.values_list('part_of__network', flat = True)
		).distinct().exclude(
			domain__iexact = request.network.parent.domain
		).only('name', 'domain').order_by('name').count()
		
		return {
			'network_memberships': networks
		}
		
	return {
		'network_memberships': 0
	}