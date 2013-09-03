#!/usr/bin/env python
# encoding: utf-8

from django.contrib import admin
from django.db import models
from meegloo.networks import models as networks

class NetworkAdmin(admin.ModelAdmin):
	list_display = (
		'name',
		'domain',
		'privacy'
	)
	
	list_filter = ('privacy',)
	
	def queryset(self, request):
		return super(NetworkAdmin, self).queryset(request).filter(
			parent = request.network.parent
		)
	
	def has_delete_permission(self, request, obj = None):
		if obj:
			return obj.domain != request.network.domain and obj.domain != request.network.parent.domain
		
		return super(NetworkAdmin, self).has_delete_permission(request, obj)
	
	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == 'parent':
			kwargs['queryset'] = networks.SuperNetwork.objects.filter(pk = request.network.parent.pk)
			kwargs['initial'] = request.network.parent
		elif db_field.name == 'owner':
			kwargs['initial'] = request.user
		
		return super(NetworkAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(networks.Network, NetworkAdmin)