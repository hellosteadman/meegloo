#!/usr/bin/env python
# encoding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('meegloo.viral.views',
	url(r'^win/$', 'register', name = 'competition_register'),
	url(r'^win/leaderboard/$', 'leaderboard', name = 'competition_leaderboard'),
	url(r'^win/(?P<guid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$', 'register', name = 'competition_register_subentrant')
)