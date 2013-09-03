#!/usr/bin/env python
# encoding: utf-8

from django.contrib import admin
from django.contrib import messages
from django.conf.urls.defaults import *
from meegloo.mail import models as mail

class MailTypeAdmin(admin.ModelAdmin):
	list_display = (
		'name', 'can_unsubscribe'
	)
	
	list_filter = ('can_unsubscribe',)

admin.site.register(mail.MailType, MailTypeAdmin)

class SectionInline(admin.StackedInline):
	model = mail.Section
	extra = 0

class MessageAdmin(admin.ModelAdmin):
	list_display = (
		'name', 'kind', 'created', 'sent'
	)
	
	list_filter = ('kind',)
	date_hierarchy = 'created'
	
	fieldsets = (
		(
			None,
			{
				'fields': ('name', 'kind')
			}
		),
		(
			u'Target users who',
			{
				'fields': (
					('filter_active', 'filter_noprofile'),
					('filter_cold', 'filter_freezing', 'filter_lurkers')
				)
			}
		),
		(
			u'Exclude users who',
			{
				'fields': ('exclude_messages',)
			}
		),
		(
			u'Message template',
			{
				'description': u'Use Django template syntax and Markdown to add dynamic data, like {{ first_name }}, {{ last_name }} or {{ last_login|date }}.',
				'fields': ('subject_template', 'header_template', 'footer_template')
			}
		)
	)
	
	inlines = [SectionInline]
	
	def get_urls(self):
		return patterns('',
			(r'^(?P<id>\d+)/send/$', self.admin_site.admin_view(self.send_view))
		) + super(MessageAdmin, self).get_urls()
	
	def send_view(self, request, id):
		from django.template.response import TemplateResponse
		from django.shortcuts import get_object_or_404
		
		obj = get_object_or_404(self.model, pk = id)
		test = True
		
		if request.method == 'POST':
			if request.POST.get('_send'):
				test = request.POST.get('test') != '0'
				
				if test:
					obj.send(request.network, request.user)
					messages.add_message(
						request,
						messages.SUCCESS,
						u'A test email was sent to %s' % request.user.email
					)
				else:
					obj.send(request.network)
					messages.add_message(
						request,
						messages.SUCCESS,
						u'Your message was emailed to %d recipient(s)' % obj.recipients.filter(test = False).count()
					)
		
		return TemplateResponse(
			request,
			'admin/mail/send_form.html',
			{
				'original': obj,
				'app_label': obj._meta.app_label,
				'opts': obj._meta,
				'recipients': obj.filter_users(),
				'test': test
			}
		)

admin.site.register(mail.Message, MessageAdmin)

class UnsubscribeAdmin(admin.ModelAdmin):
	list_display = ('user', 'kind', 'unsubscribed')
	list_filter = ('kind',)
	readonly_fields = ('user', 'kind')
	date_hierarchy = 'unsubscribed'

admin.site.register(mail.Unsubscribe, UnsubscribeAdmin)