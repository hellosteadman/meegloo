#!/usr/bin/env python
# encoding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('meegloo.oembed.views',
	url(r'^(?P<handler>[\w]+)/$', 'html', name = 'oembed_html'),
)