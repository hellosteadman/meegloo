#!/usr/bin/env python
# encoding: utf-8

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.template.defaultfilters import truncatewords
from django import forms
from meegloo.streams import models as streams

class StreamAdmin(admin.ModelAdmin):
	list_display = (
		'name',
		'slug',
		'start',
		'end',
		'contributor_count',
		'post_count'
	)
	
	list_filter = (
		'network',
	)
	
	date_hierarchy = 'start'
	
	def queryset(self, request):
		return super(StreamAdmin, self).queryset(request).filter(
			network__parent = request.network.parent
		).summary()
	
	def contributor_count(self, obj):
		url = '%s?part_of__id__exact=%d' % (
			reverse('admin:streams_userstream_changelist'), obj.pk
		)
		
		if obj.contributor_count > 0:
			title = '%d contributor' % obj.contributor_count + (obj.contributor_count != 1 and 's' or '')
		else:
			title = 'No contributor'
		
		return '<a href="%s">%s</a>' % (url, title)
	contributor_count.allow_tags = True
	contributor_count.short_description = 'Contributors'
	contributor_count.admin_order_field = 'contributor_count'
	
	def post_count(self, obj):
		url = '%s?stream__part_of__id__exact=%d' % (
			reverse('admin:streams_post_changelist'), obj.pk
		)
		
		if obj.post_count > 0:
			title = '%d post' % obj.post_count + (obj.post_count != 1 and 's' or '')
		else:
			title = 'No posts'
		
		return '<a href="%s">%s</a>' % (url, title)
	post_count.allow_tags = True
	post_count.short_description = 'Posts'
	post_count.admin_order_field = 'post_count'
		
admin.site.register(streams.Stream, StreamAdmin)

class UserStreamAdmin(admin.ModelAdmin):
	list_display = (
		'profile',
		'part_of',
		'public',
		'updated',
		'post_count'
	)
	
	date_hierarchy = 'updated'
	list_filter = ('part_of',)
	readonly_fields = ('part_of', 'profile', 'updated')
	
	def queryset(self, request):
		return super(UserStreamAdmin, self).queryset(request).filter(
			part_of__network__parent = request.network.parent
		).summary()
	
	def public(self, obj):
		return not obj.private
	public.boolean = True
	
	def has_add_permission(self, request):
		return False
	
	def post_count(self, obj):
		url = '%s?stream__id__exact=%d' % (
			reverse('admin:streams_post_changelist'), obj.pk
		)
		
		if obj.post_count > 0:
			title = '%d post' % obj.post_count + (obj.post_count != 1 and 's' or '')
		else:
			title = 'No posts'
		
		return '<a href="%s">%s</a>' % (url, title)
	post_count.allow_tags = True
	post_count.short_description = 'Posts'
	post_count.admin_order_field = 'post_count'

admin.site.register(streams.UserStream, UserStreamAdmin)

class PostMediaInline(admin.TabularInline):
	model = streams.Media
	extra = 0

class PostAdmin(admin.ModelAdmin):
	list_display = (
		'truncated',
		'posted',
		'author',
		'kind'
	)
	
	list_filter = ('kind', 'state', 'stream__part_of')
	date_hierarchy = 'posted'
	
	readonly_fields = ('stream', 'posted', 'kind', 'author', 'area', 'tweet', 'state')
	exclude = ('guid', 'tags')
	
	fields = (
		'stream', 'posted',
		'text', 'kind', 'author',
		'latitude', 'longitude', 'area',
		'tweet', 'state'
	)
	
	inlines = [PostMediaInline]
	
	def has_add_permission(self, request):
		return False
	
	def formfield_for_dbfield(self, db_field, **kwargs):
		if db_field.name == 'text':
			kwargs['widget'] = forms.Textarea
		
		return super(PostAdmin, self).formfield_for_dbfield(db_field, **kwargs)
	
	def queryset(self, request):
		return super(PostAdmin, self).queryset(request).filter(
			stream__part_of__network__parent = request.network.parent
		)
	
	def truncated(self, obj):
		text = truncatewords(unicode(obj), 10)
		
		if len(text) > 46:
			text = text[:46] + ' ...'
		
		return text

admin.site.register(streams.Post, PostAdmin)