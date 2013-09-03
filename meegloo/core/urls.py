#!/usr/bin/env python
# encoding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('meegloo.core.views',
	url(r'^search/', 'search', name = 'search'),
)