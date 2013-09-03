#!/usr/bin/env python
# encoding: utf-8

from django.db import models
from django.db.models import Count
from django.template.loader import Template, Context, render_to_string
from django.conf import settings
from django.core.mail import get_connection, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from meegloo.core.models import Profile
from meegloo.mail import helpers
from sorl.thumbnail import get_thumbnail
from markdown import markdown
from datetime import datetime, timedelta
from uuid import uuid4
import logging

FROM_EMAIL = getattr(settings, 'DEFAULT_FROM_EMAIL', 'hello@meegloo.com')

class MailType(models.Model):
	name = models.CharField(max_length = 50)
	can_unsubscribe = models.BooleanField(u'recipients can unsubscribe', default = True)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ('name',)
		db_table = 'mail_type'

class Message(models.Model):
	name = models.CharField(max_length = 50)
	kind = models.ForeignKey('MailType', related_name = 'messages')
	
	filter_active = models.BooleanField(verbose_name = u'are active', default = True)
	filter_lurkers = models.BooleanField(verbose_name = u'haven\'t posted yet', default = False)
	filter_cold = models.BooleanField(verbose_name = u'haven\'t posted for a month')
	filter_freezing = models.BooleanField(verbose_name = u'haven\'t posted for 3 months')
	filter_noprofile = models.BooleanField(verbose_name = u'with an empty profile', default = False)
	exclude_messages = models.ManyToManyField('self', null = True, blank = True,
		verbose_name = u'have received these messages',
		db_table = 'mail_message_exclude'
	)
	
	subject_template = models.CharField(max_length = 500, verbose_name = 'subject')
	header_template = models.TextField(verbose_name = 'header')
	footer_template = models.TextField(verbose_name = 'footer')
	
	created = models.DateTimeField(editable = False)
	sent = models.DateTimeField(editable = False, null = True)
	
	def __unicode__(self):
		return self.name
	
	def save(self, *args, **kwargs):
		if not self.created:
			self.created = datetime.now()
		
		super(Message, self).save(*args, **kwargs)
	
	def filter_users(self):
		users = User.objects.all()
		
		if self.filter_active:
			users = users.filter(is_active = True)
		
		if self.filter_lurkers:
			users = users.annotate(
				post_count = Count('posts')
			).filter(
				post_count = 0
			)
		
		datediff = 'SELECT DATEDIFF(NOW(), `posted`) FROM `streams_post` ' \
			'WHERE `author_id` = `auth_user`.`id` ' \
			'ORDER BY `posted` DESC LIMIT 1'
		
		count = 'SELECT COUNT(*) FROM `streams_post` ' \
			'WHERE `author_id` = `auth_user`.`id`'
		
		if self.filter_cold:
			users = users.filter(
				date_joined__lte = datetime.now() - timedelta(days = 30)
			).extra(
				where = [
					'((%s) >= 30 OR (%s) = 0)' % (datediff, count)
				]
			)
		
		if self.filter_freezing:
			users = users.filter(
				date_joined__lte = datetime.now() - timedelta(days = 90)
			).extra(
				where = [
					'((%s) >= 90 OR (%s) = 0)' % (datediff, count)
				]
			)
		
		if self.filter_noprofile:
			users = users.annotate(
				profile_count = Count('profiles')
			).filter(
				profile_count = 0
			)
		
		if self.exclude_messages.count() > 0:
			users = users.exclude(
				messages__message__in = self.exclude_messages.all()
			)
		
		users = users.exclude(
			unsubscribes__kind = self.kind
		)
		
		return users
	
	def send(self, network, test_user = None):
		subject_template = Template(self.subject_template)
		header_template = Template(self.header_template)
		footer_template = Template(self.footer_template)
		logger = logging.getLogger()
		emails = []
		
		context = {
			'network': network,
			'MEDIA_URL': getattr(settings, 'MEDIA_URL', '/media/'),
		}
		
		if not test_user:
			if self.sent:
				raise Exception('Message already sent')
			
			if self.recipients.filter(test = False).count() > 0:
				raise Exception('Message already has recipients')
			
			for user in self.filter_users():
				self.recipients.create(user = user)
			
			for user in self.recipients.filter(test = False):
				emails.append(
					user.prepare_email(
						context, subject_template, header_template, footer_template
					)
				)
			
			self.sent = datetime.now()
			super(Message, self).save()
		else:
			user = self.recipients.create(
				user = test_user, test = True
			)
			
			emails.append(
				user.prepare_email(
					context, subject_template, header_template, footer_template
				)
			)
		
		connection = get_connection()
		connection.send_messages(emails)
		logger.info('Sent email to %d recipients' % len(emails))
	
	class Meta:
		ordering = ('-created',)

class Section(models.Model):
	message = models.ForeignKey('Message', related_name = 'sections')
	image = models.ImageField(upload_to = helpers.upload_section_image)
	title_template = models.CharField(max_length = 500, verbose_name = u'title')
	body_template = models.TextField(verbose_name = u'body')
	order = models.PositiveIntegerField()
	
	def __unicode__(self):
		return self.title_template
	
	class Meta:
		ordering = ('order',)

class Recipient(models.Model):
	guid = models.CharField(max_length = 36)
	message = models.ForeignKey('Message', related_name = 'recipients')
	user = models.ForeignKey('auth.User', related_name = 'messages')
	sent = models.DateTimeField(null = True)
	test = models.BooleanField(default = False)
	
	def save(self, *args, **kwargs):
		if not self.guid:
			self.guid = str(uuid4())
		
		super(Recipient, self).save(*args, **kwargs)
	
	def prepare_email(self, base_context, subject_template, header_template, footer_template):
		try:
			profile = self.user.get_profile()
		except Profile.DoesNotExist:
			profile = None
		
		context = Context(
			{
				'first_name': self.user.first_name,
				'last_name': self.user.last_name,
				'username': self.user.username,
				'email': self.user.email,
				'is_staff': self.user.is_staff,
				'is_active': self.user.is_active,
				'is_superuser': self.user.is_superuser,
				'last_login': self.user.last_login,
				'date_joined': self.user.date_joined,
				'profile': profile
			}
		)
		
		subject = subject_template.render(context)
		sections = []
		
		for section in self.message.sections.all():
			sections.append(
				{
					'title': Template(section.title_template).render(context),
					'body': Template(section.body_template).render(context),
					'image': get_thumbnail(section.image, '150x150', crop = 'center')
				}
			)
		
		base_context['unsubscribe_url'] = 'http://%s%s' % (
			base_context['network'].domain,
			reverse('mail_unsubscribe', args = [self.guid])
		)
		
		header = header_template.render(context)
		footer = footer_template.render(context)
		
		base_context['body'] = render_to_string('email/sections.inc.txt',
			{
				'header': header,
				'sections': sections,
				'footer': footer
			}
		)
		
		email = EmailMultiAlternatives(
			subject,
			render_to_string('email/base.txt', base_context),
			'Meegloo mail <%s>' % FROM_EMAIL,
			[
				self.user.first_name and (
					'%s %s <%s>' % (self.user.first_name, self.user.last_name, self.user.email)
				) or self.user.email
			]
		)
		
		base_context['body'] = render_to_string('email/sections.inc.html',
			{
				'header': header,
				'sections': sections,
				'footer': footer
			}
		)
		
		email.attach_alternative(
			render_to_string('email/base.html', base_context),
			'text/html'
		)
		
		return email
	
	class Meta:
		ordering = ('-sent',)

class Unsubscribe(models.Model):
	kind = models.ForeignKey('MailType', related_name = 'unsubscribes')
	user = models.ForeignKey('auth.User', related_name = 'unsubscribes')
	unsubscribed = models.DateTimeField(auto_now_add = True)
	
	def __unicode__(self):
		return u'%s from %s' % (self.user, self.kind.name)
	
	class Meta:
		ordering = ('-unsubscribed',)