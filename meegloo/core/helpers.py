#!/usr/bin/env python
# encoding: utf-8

import logging
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User
from django.conf import settings

def render_to_mail(network, subject, template, context, recipient, fail_silently = False):
	from_email = getattr(settings, 'DEFAULT_FROM_EMAIL')
	
	if isinstance(recipient, User):
		recipients = [recipient.email]
	elif isinstance(recipient, (str, unicode)):
		recipients = [recipient]
	elif isinstance(recipient, (list, tuple)):
		recipients = recipient
	else:
		raise Exception('recipient argument must be User, string, list or tuple')
	
	ctx = {
		'network': network,
		'MEDIA_URL': getattr(settings, 'MEDIA_URL', '/media/'),
		'template': template
	}
	
	ctx.update(context)
	
	email = EmailMultiAlternatives(
		subject,
		render_to_string('email/base.txt', ctx),
		from_email, recipients
	)
	
	email.attach_alternative(
		render_to_string('email/base.html', ctx),
		"text/html"
	)
	
	logger = logging.getLogger()
	
	try:
		email.send()
		logger.info('Sent email to %s from %s' % (', '.join(recipients), from_email))
	except:
		if not fail_silently:
			raise

def upload_avatar(instance, filename):
	from os import path
	
	return '%s/%s%s' % (
		'avatars',
		instance.user.username.lower(),
		path.splitext(filename)[-1]
	)