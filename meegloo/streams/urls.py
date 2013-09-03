#!/usr/bin/env python
# encoding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('meegloo.streams.views',
	url(r'^$', 'posts', name = 'posts'),
	url(r'^feed\.rss$', 'posts', {'format': 'rss'}, name = 'user_rss'),
	url(r'^feed\.atom$', 'posts', {'format': 'atom'}, name = 'user_atom'),
	url(r'^streams\.js$', 'my_streams', name = 'streams_json'),
	url(r'^create/$', 'create', name = 'create_stream'),
	url(r'^join/$', 'streams', name = 'streams'),
	url(r'^categories/(?P<category>[\/\w-]+)/$', 'posts', name = 'category_posts'),
	url(r'^(?P<slug>[\w-]+)/join/$', 'join', name = 'join_stream'),
	url(r'^(?P<slug>[\w-]+)/edit/$', 'edit', name = 'edit_stream'),
	url(r'^(?P<slug>[\w-]+)/leave/$', 'leave', name = 'leave_stream'),
	url(r'^(?P<stream>[\w-]+)/$', 'posts', name = 'stream'),
	url(r'^(?P<stream>[\w-]+)/embed\.js$', 'posts', {'format': 'embed'}, name = 'embed_stream'),
	url(r'^(?P<stream>[\w-]+)/embed\.html$', 'posts', {'format': 'iframe'}, name = 'embed_stream'),
	url(r'^(?P<stream>[\w-]+)/feed\.rss$', 'posts', {'format': 'rss'}, name = 'stream_rss'),
	url(r'^(?P<stream>[\w-]+)/feed\.atom$', 'posts', {'format': 'atom'}, name = 'stream_atom'),
	url(r'^(?P<slug>[\w-]+)/embed/$', 'embed', name = 'embed_stream_options'),
	url(r'^(?P<stream>[\w-]+)/(?P<kind>audio|video|photo|text)/$', 'posts', name = 'stream_by_type'),
	url(r'^(?P<stream>[\w-]+)/(?P<kind>audio|video|photo|text)/feed\.rss$', 'posts', name = 'stream_by_type_rss'),
	url(r'^(?P<stream>[\w-]+)/posts/(?P<pk>\d+)/$', 'post', name = 'stream_post'),
	url(r'^(?P<stream>[\w-]+)/posts/(?P<pk>\d+)/embed/$', 'post', {'format': 'embed'}, name = 'embed_post'),
	url(r'^(?P<stream>[\w-]+)/sets/(?P<pk>\d+)/$', 'set', name = 'stream_set')
)