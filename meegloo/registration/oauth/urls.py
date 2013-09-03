#!/usr/bin/env python
# encoding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('meegloo.registration.oauth.views',
	url(r'^(?P<site>[\w]+)/auth/$', 'auth', name = 'oauth_auth'),
	url(r'^(?P<site>[\w]+)/return/$', 'return_auth', name = 'oauth_return'),
	url(r'^(?P<site>[\w]+)/clear/$', 'unauth', name = 'oauth_unauth'),
	url(r'^(?P<site>[\w]+)/connect/$', 'connect', name = 'oauth_connect'),
	url(r'^(?P<site>[\w]+)/connect\.json$', 'connect_json', name = 'oauth_connect_json')
)