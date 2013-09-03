#!/usr/bin/env python
# encoding: utf-8

from django.contrib import admin
from meegloo.social import models as social

class CommentAdmin(admin.ModelAdmin):
	list_display = (
		'__unicode__',
		'content_type',
		'author',
		'posted'
	)
	
	list_filter = (
		'content_type',
		'network',
	)
	
	date_hierarchy = 'posted'
	
	def queryset(self, request):
		return super(CommentAdmin, self).queryset(request).filter(
			network__parent = request.network.parent
		)
		
admin.site.register(social.Comment, CommentAdmin)