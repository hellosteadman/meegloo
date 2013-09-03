#!/usr/bin/env python
# encoding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('meegloo.uploadify.views',
	url(r'upload/$', 'upload', name = 'uploadify_upload'),
)