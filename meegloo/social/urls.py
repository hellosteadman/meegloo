#!/usr/bin/env python
# encoding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('meegloo.social.views',
	url(r'comment/(?P<app_label>[\w]+)/(?P<model>[\w]+)/(?P<object_id>\d+)/$', 'post_comment', name = 'post_comment'),
	url(r'question/(?P<app_label>[\w]+)/(?P<model>[\w]+)/(?P<object_id>\d+)/$', 'answer_question', name = 'answer_question')
)