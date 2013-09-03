#!/usr/bin/env python
# encoding: utf-8

from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.utils import simplejson
from django.contrib.auth.decorators import login_required
from meegloo.networks.models import Network

def networks(request):
	return TemplateResponse(
		request,
		'networks/list.html',
		{
			'networks': Network.objects.filter(
				parent = request.network.parent
			).public().external(),
			'body_classes': ('networks',),
			'title_parts': (u'Discover networks',)
		}
	)

@login_required
def my_networks(request):
	from django.utils import simplejson
	
	networks = Network.objects.filter(
		parent = request.network.parent,
		pk__in = request.user.streams.values_list('part_of__network', flat = True)
	).distinct().exclude(
		domain__iexact = request.network.parent.domain
	).values('name', 'domain').order_by('name')
	
	return HttpResponse(
		simplejson.dumps([n for n in networks]),
		mimetype = 'application/json'
	)