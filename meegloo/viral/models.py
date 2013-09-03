#!/usr/bin/env python
# encoding: utf-8

from django.db import models
from django.db.models import Count, Sum, signals
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from meegloo.viral import helpers, managers
from meegloo.streams.models import Post, UserStream
from meegloo.social.models import Comment, Answer
from datetime import datetime
from uuid import uuid4

class Competition(models.Model):
	headline = models.CharField(max_length = 50)
	subheading = models.CharField(max_length = 300)
	start = models.DateField()
	deadline = models.DateField()
	body = models.TextField()
	terms = models.TextField()
	network = models.ForeignKey('networks.Network', related_name = 'competitions')
	objects = managers.CompetitionManager()
	
	def __unicode__(self):
		return self.headline
	
	def is_active(self):
		now = datetime.now().date()
		return self.start <= now and self.deadline > now
	
	def days_remaining(self):
		return (self.deadline - datetime.now().date()).days
	
	class QuerySet(models.query.QuerySet):
		def active(self):
			return self.exclude(
				start__gt = datetime.now(),
				deadline__lt = datetime.now()
			)
		
		def summary(self):
			return self.annotate(
				entrant_count = Count('entrants')
			)
	
	class Meta:
		ordering = ('-start',)
		get_latest_by = 'start'

class Entrant(models.Model):
	competition = models.ForeignKey('Competition', related_name = 'entrants')
	guid = models.CharField(u'GUID', max_length = 36, unique = True, editable = False)
	user = models.ForeignKey('auth.User', related_name = 'competition_entries')
	parent = models.ForeignKey('self', related_name = 'subentrants', null = True, blank = True)
	barred = models.BooleanField()
	entered = models.DateTimeField(auto_now_add = True)
	objects = managers.EntrantManager()
	
	def __unicode__(self):
		return self.user.get_full_name() or self.user.username
	
	def is_valid(self):
		return not self.barred and self.user.is_active
	
	def save(self, *args, **kwargs):
		if not self.guid:
			self.guid = str(uuid4())
		
		super(Entrant, self).save(*args, **kwargs)
	
	class QuerySet(models.query.QuerySet):
		def active(self):
			from datetime import datetime
			
			return self.exclude(
				competition__start__gt = datetime.now(),
				competition__deadline__lt = datetime.now()
			)
		
		def eligible(self):
			return self.filter(
				user__is_active = True,
# 				user__is_staff = False,
# 				user__is_superuser = False,
				barred = False
			)
		
		def leaderboard(self):
			return self.eligible().annotate(
				points = Sum('actions__points')
			).filter(
				points__gt = 0
			).order_by('-points')
		
		def summary(self):
			return self.annotate(
				point_count = Sum('actions__points')
			)
	
	class Meta:
		ordering = ('-entered',)
		get_latest_by = 'entered'

class Action(models.Model):
	entrant = models.ForeignKey('Entrant', related_name = 'actions')
	text = models.CharField(max_length = 200)
	points = models.PositiveIntegerField()
	content_type = models.ForeignKey('contenttypes.ContentType', related_name = 'competition_actions')
	object_id = models.PositiveIntegerField()
	content_object = generic.GenericForeignKey()
	performed = models.DateTimeField(auto_now_add = True)
	
	def __unicode__(self):
		return self.text
	
	def save(self, *args, **kwargs):
		new = not self.pk
		super(Action, self).save(*args, **kwargs)
		
		if new:
			if not self.entrant.parent is None and self.points >= 1:
				points = self.points / 5.0
				self.entrant.parent.actions.create(
					text = u'Kickback from %s' % self.entrant.user.username,
					content_type = ContentType.objects.get_for_model(self),
					object_id = self.pk,
					points = points
				)
				
	class Meta:
		ordering = ('-performed',)
		get_latest_by = 'performed'
		unique_together = ('content_type', 'object_id')

signals.post_save.connect(helpers.post_post_save, sender = Post)
signals.post_save.connect(helpers.stream_post_save, sender = UserStream)
signals.post_save.connect(helpers.comment_post_save, sender = Comment)
signals.post_save.connect(helpers.answer_post_save, sender = Answer)