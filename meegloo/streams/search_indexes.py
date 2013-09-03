#!/usr/bin/env python
# encoding: utf-8

import datetime
from haystack import site
from haystack.indexes import *
from meegloo.streams import POST_LIVE
from meegloo.streams.models import Post

class PostIndex(SearchIndex):
	text = CharField(document = True, model_attr = 'text')
	author = CharField(model_attr = 'author')
	stream = CharField(model_attr = 'stream')
	network = CharField(model_attr = 'stream__part_of__network__parent')
	kind = CharField(model_attr = 'kind')
	posted = DateTimeField(model_attr = 'posted')
	
	def index_queryset(self):
		return Post.objects.filter(
			stream__private = False,
			state = POST_LIVE
		)

site.register(Post, PostIndex)