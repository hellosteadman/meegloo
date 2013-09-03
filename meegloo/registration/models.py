#!/usr/bin/env python
# encoding: utf-8

from django.db import models

class EmailConfirmation(models.Model):
	user = models.ForeignKey('auth.User', related_name = 'email_confirmations')
	guid = models.CharField(max_length = 36, unique = True)
	email = models.EmailField()
	sent = models.DateTimeField(auto_now_add = True)
	network = models.ForeignKey('networks.Network', related_name = 'email_confirmations')
	
	def __unicode__(self):
		return self.email
	
	def get_absolute_url(self):
		from django.core.urlresolvers import reverse
		
		return '%s?guid=%s' % (
			reverse('confirm_email'),
			self.guid
		)
	
	def save(self, *args, **kwargs):
		from meegloo.core.helpers import render_to_mail
		
		if not self.guid:
			from uuid import uuid4
			self.guid = str(uuid4())
		
		if not self.email:
			self.email = self.user.email
		
		if not self.pk:
			self.user.is_active = False
			self.user.save()
		
		render_to_mail(
			self.network,
			u'Confirm your email address',
			self.user.email == self.email and 'email/confirm.txt' or 'email/reconfirm.txt',
			{
				'confirmation': self
			},
			self.email
		)
		
		super(EmailConfirmation, self).save(*args, **kwargs)
	
	def confirm(self):
		self.user.is_active = True
		self.user.email = self.email
		self.user.save()
		
		self.delete()
	
	class Meta:
		get_latest_by = 'sent'

class PasswordReset(models.Model):
	user = models.ForeignKey('auth.User', related_name = 'password_resets')
	guid = models.CharField(max_length = 36, unique = True)
	sent = models.DateTimeField(auto_now_add = True)
	expires = models.DateTimeField()
	network = models.ForeignKey('networks.Network', related_name = 'password_resets')
	
	def __unicode__(self):
		return self.user
	
	def get_absolute_url(self):
		from django.core.urlresolvers import reverse
		
		return '%s?guid=%s' % (
			reverse('reset_password'),
			self.guid
		)
	
	def save(self, *args, **kwargs):
		from meegloo.core.helpers import render_to_mail
		from datetime import datetime, timedelta
		
		if not self.guid:
			from uuid import uuid4
			self.guid = str(uuid4())
		
		if not self.expires:
			self.expires = datetime.now() + timedelta(hours = 24)
		
		if not self.pk:
			render_to_mail(
				self.network,
				u'Reset your password',
				'email/reset.txt',
				{
					'request': self
				},
				self.user.email
			)
		
		super(PasswordReset, self).save(*args, **kwargs)
	
	def reset(self, password):
		self.user.set_password(password)
		self.user.save()
		
		self.delete()
	
	class Meta:
		get_latest_by = 'sent'