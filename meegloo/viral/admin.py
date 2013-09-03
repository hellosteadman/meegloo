#!/usr/bin/env python
# encoding: utf-8

from django.contrib import admin
from django.core.urlresolvers import reverse
from meegloo.viral import models as viral

class CompetitionAdmin(admin.ModelAdmin):
	list_display = ('headline', 'start', 'deadline', 'entrant_count')
	list_filter = ('network',)
	
	def queryset(self, request):
		return super(CompetitionAdmin, self).queryset(request).filter(
			network__parent = request.network.parent
		).summary()
		
	def entrant_count(self, obj):
		url = '%s?competition__id__exact=%d' % (
			reverse('admin:viral_entrant_changelist'), obj.pk
		)
		
		if obj.entrant_count > 0:
			title = '%d entrant' % obj.entrant_count + (obj.entrant_count != 1 and 's' or '')
		else:
			title = 'No entrants'
		
		return '<a href="%s">%s</a>' % (url, title)
	entrant_count.allow_tags = True
	entrant_count.short_description = 'Entrants'
	entrant_count.admin_order_field = 'entrant_count'

admin.site.register(viral.Competition, CompetitionAdmin)

class EntrantAdmin(admin.ModelAdmin):
	list_display = ('user', 'competition', 'point_count')
	list_filter = ('competition',)
	readonly_fields = ('guid',)
	
	def has_add_permission(self, request):
		return False
	
	def queryset(self, request):
		return super(EntrantAdmin, self).queryset(request).filter(
			competition__network__parent = request.network.parent
		).summary()
	
	def point_count(self, obj):
		if obj.point_count > 0:
			return '%d point' % obj.point_count + (obj.point_count != 1 and 's' or '')
		else:
			return 'No points'
	point_count.short_description = 'Points'
	point_count.admin_order_field = 'point_count'

admin.site.register(viral.Entrant, EntrantAdmin)

class ActionAdmin(admin.ModelAdmin):
	list_display = ('entrant', 'competition', 'text', 'points', 'performed')
	list_filter = ('entrant__competition',)
	
	def queryset(self, request):
		return super(ActionAdmin, self).queryset(request).filter(
			entrant__competition__network__parent = request.network.parent
		)
	
	def competition(self, obj):
		return obj.entrant.competition
	competition.short_description = 'Competition'
	competition.admin_order_field = 'entrant__competition__name'

admin.site.register(viral.Action, ActionAdmin)