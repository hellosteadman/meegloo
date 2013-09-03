#!/usr/bin/env python
# encoding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('meegloo.networks.views',
	url(r'^networks/$', 'networks', name = 'networks'),
	url(r'^networks\.js$', 'my_networks', name = 'networks_json'),
)