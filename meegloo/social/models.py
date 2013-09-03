#!/usr/bin/env python
# encoding: utf-8

from django.db import models
from django.contrib.contenttypes import generic
from datetime import datetime

class Comment(models.Model):
	content_type = models.ForeignKey(
		'contenttypes.ContentType', related_name = 'comments', editable = False
	)
	
	object_id = models.PositiveIntegerField(editable = False)
	content_object = generic.GenericForeignKey()
	author = models.ForeignKey('auth.User', related_name = 'comments')
	network = models.ForeignKey('networks.Network', related_name = 'comments')
	posted = models.DateTimeField()
	text = models.TextField()
	tweet = models.BooleanField()
	
	def __unicode__(self):
		return unicode(self.content_object)
	
	def get_absolute_url(self):
		return '%s#comment-%d' % (
			self.content_object.get_absolute_url(), self.pk
		)
	
	def update_twitter(self):
		from django.conf import settings
		from meegloo.core.models import OAuthToken
		from meegloo.urlshortening.helpers import shorten
		from meegloo.social.helpers import format_tweet
		from twitter import Api
		import logging
		
		oauth_creds = getattr(settings, 'OAUTH_CREDENTIALS').get('TWITTER')
		logger = logging.getLogger()
		
		try:
			token = self.author.oauth_tokens.get(site = 'twitter')
		except OAuthToken.DoesNotExist:
			logger.debug('No OAuth token for %s' % self.author.username)
			return
		
		api = Api(
			consumer_key = oauth_creds.get('CONSUMER_KEY'),
			consumer_secret = oauth_creds.get('CONSUMER_SECRET'),
			access_token_key = token.token,
			access_token_secret = token.secret
		)
		
		if hasattr(self.content_object, 'get_twitter_tags'):
			tags = ['#%s' % s for s in self.content_object.get_twitter_tags()]
		else:
			tags = []
		
		url = shorten(self, self.network, self.author)
		tweet = format_tweet(self.text, tags, url)
		
		try:
			api.PostUpdate(tweet)
		except Exception, ex:
			logger.error('Unable to post tweet', exc_info = ex)
	
	def save(self, *args, **kwargs):
		if not self.posted:
			self.posted = datetime.now()
		
		new = not self.pk
		super(Comment, self).save(*args, **kwargs)
		
		if new and self.tweet:
			self.update_twitter()
		
	class Meta:
		ordering = ('-posted',)
		get_latest_by = 'posted'

class Question(models.Model):
	content_type = models.ForeignKey(
		'contenttypes.ContentType', editable = False
	)
	
	object_id = models.PositiveIntegerField(editable = False)
	content_object = generic.GenericForeignKey()
	prompt = models.TextField()
	
	def __unicode__(self):
		return self.prompt
		
	class Meta:
		unique_together = ('content_type', 'object_id')

class Poll(Question):
	pass

class PollOption(models.Model):
	poll = models.ForeignKey('Poll', related_name = 'options')
	label = models.CharField(max_length = 200)
	order = models.PositiveIntegerField()
	
	def __unicode__(self):
		return self.label
	
	class Meta:
		db_table = 'social_poll_option'
		ordering = ('order',)

class Answer(models.Model):
	question = models.ForeignKey('Question', related_name = 'answers')
	user = models.ForeignKey('auth.User', related_name = 'poll_answers')
	answered = models.DateTimeField()
	text = models.TextField()
	
	def __unicode__(self):
		return self.text
	
	def save(self, *args, **kwargs):
		if not self.answered:
			from datetime import datetime
			
			self.answered = datetime.now()
		
		super(Answer, self).save(*args, **kwargs)

class PollAnswer(Answer):
	option = models.ForeignKey('PollOption', related_name = 'answers')
	
	class Meta:
		db_table = 'social_poll_answer'

class Follow(models.Model):
	follower = models.ForeignKey('auth.User', related_name = 'following')
	followee = models.ForeignKey('auth.User', related_name = 'followers')
	followed = models.DateTimeField(auto_now_add = True)
	
	def __unicode__(self):
		return u'%s > %s' % (self.follower, self.followee)
	
	def notify(self, network):
		from meegloo.core.helpers import render_to_mail
		
		render_to_mail(
			network,
			u'You have a new follower on Meegloo!',
			'email/followed.txt',
			{
				'follow': self
			},
			self.followee
		)
	
	class Meta:
		ordering = ('-followed',)
		unique_together = ('follower', 'followee')