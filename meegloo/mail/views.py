#!/usr/bin/env python
# encoding: utf-8

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.db.models import Q
from django.contrib.auth.models import User
from meegloo.mail.models import Recipient, Unsubscribe, MailType

def unsubscribe(request, guid):
	if request.method == 'GET':
		try:
			recipient = Recipient.objects.get(
				guid = guid,
				message__kind__can_unsubscribe = True
			)
			
			if not recipient.test:
				unsubscribe, created = Unsubscribe.objects.get_or_create(
					user = recipient.user,
					kind = recipient.message.kind
				)
			else:
				created = False
			
			return TemplateResponse(
				request,
				'mail/unsubscribed.html',
				{
					'kind': recipient.message.kind,
					'created': created
				}
			)
		except Recipient.DoesNotExist:
			pass
	elif request.POST.get('name'):
		name = request.POST['name']
		q = Q(username__iexact = name) | Q(email__iexact = name)
		
		try:
			user = User.objects.get(q)
			
			for kind in MailType.objects.filter(can_unsubscribe = True):
				unsubscribe, created = Unsubscribe.objects.get_or_create(
					user = user,
					kind = kind
				)
			
			return TemplateResponse(
				request,
				'mail/unsubscribed.html'
			)
		except User.DoesNotExist:
			pass
	
	return TemplateResponse(
		request,
		'mail/unsubscribe.html'
	)