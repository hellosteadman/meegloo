#!/usr/bin/env python
# encoding: utf-8

import datetime
from haystack import site
from haystack.indexes import *
from meegloo.networks.models import Network

class NetworkIndex(SearchIndex):
	text = CharField(document = True)
	name = CharField(model_attr = 'name')
	domain = CharField(model_attr = 'domain')
	network = CharField(model_attr = 'parent')
	
	def prepare_text(self, obj):
		return obj.description or obj.name
	
	def index_queryset(self):
		return Network.objects.filter(
			privacy = 1
		)

site.register(Network, NetworkIndex)