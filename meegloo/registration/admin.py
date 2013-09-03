#!/usr/bin/env python
# encoding: utf-8

from django.contrib import admin
from meegloo.registration import models as registration

class EmailConfirmationAdmin(admin.ModelAdmin):
	list_display = (
		'email',
		'user',
		'sent'
	)
	
	date_hierarchy = 'sent'
	
	def queryset(self, request):
		return super(EmailConfirmationAdmin, self).queryset(request).filter(
			network__parent = request.network.parent
		)

admin.site.register(registration.EmailConfirmation, EmailConfirmationAdmin)