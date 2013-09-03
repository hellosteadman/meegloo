#!/usr/bin/env python
# encoding: utf-8

from django.db import models
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError
from meegloo.streams import POST_TYPES, POST_STATES, POST_LIVE, POST_CONVERTING, helpers, managers
from taggit.managers import TaggableManager
import logging

class Category(models.Model):
	name = models.CharField(max_length = 50)
	slug = models.SlugField(max_length = 50)
	parent = models.ForeignKey('self', null = True)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ('name',)

class Stream(models.Model):
	name = models.CharField(max_length = 50)
	slug = models.SlugField(max_length = 20)
	network = models.ForeignKey('networks.Network', related_name = 'streams')
	description = models.CharField(max_length = 200, null = True, blank = True)
	category = models.ForeignKey('Category', related_name = 'streams', default = 5)
	start = models.DateTimeField(auto_now_add = True)
	end = models.DateTimeField(null = True, blank = True)
	updated = models.DateTimeField(auto_now_add = True)
	objects = managers.StreamManager()
	
	def clean(self):
		from django.conf import settings
		import re
		
		if not re.match(r'^[\w-]+$', self.slug):
			raise ValidationError('Enter a valid slug.')
		
		if self.slug in getattr(settings, 'INVALID_SLUGS', []):
			raise ValidationError('%s is not a valid stream URL.' % self.slug)
	
	def latest_post(self):
		return Post.objects.filter(
			stream__part_of = self,
			stream__private = False
		).latest()
	
	def __unicode__(self):
		return self.name
	
	def get_full_base_url(self):
		return 'http://%s%s' % (self.network.domain, self.get_absolute_url())
	
	def get_embed_code(self, base_url = None):
		if not base_url:
			base_url = self.get_full_base_url()
		
		from django.core.urlresolvers import reverse
		return '<script src="%sembed.js"></script>' % base_url
	
	def save(self, *args, **kwargs):
		from datetime import datetime, timedelta
		
		if self.updated:
			self.end = self.updated + timedelta(days = 1)
		else:
			self.end = datetime.now() + timedelta(days = 1)
		
		super(Stream, self).save(*args, **kwargs)
	
	def get_twitter_tags(self, author = None):
		tags = StreamTag.objects.filter(
			stream = self,
			domain = 'twitter.com'
		)
		
		if author:
			tags = tags.filter(user = author)
		
		return tags.values_list('tag', flat = True)
	
	def update_twitter(self, author):
		from django.conf import settings
		from meegloo.core.models import OAuthToken
		from meegloo.urlshortening.helpers import shorten
		from meegloo.social.helpers import format_tweet
		from twitter import Api
		
		oauth_creds = getattr(settings, 'OAUTH_CREDENTIALS').get('TWITTER')
		logger = logging.getLogger()
		
		api = Api(
			consumer_key = oauth_creds.get('CONSUMER_KEY'),
			consumer_secret = oauth_creds.get('CONSUMER_SECRET'),
			access_token_key = oauth_creds.get('BOT_TOKEN'),
			access_token_secret = oauth_creds.get('BOT_SECRET')
		)
		
		try:
			username = '@' + author.oauth_tokens.get(site = 'twitter').username
		except OAuthToken.DoesNotExist:
			username = author.get_full_name() or author.username
		
		tags = self.get_twitter_tags(author)
		url = shorten(self, self.network, author)
		text = '%s - Covered by %s' % (self.name, username)
		tweet = format_tweet(text, tags, url)
		
		try:
			api.PostUpdate(tweet)
		except Exception, ex:
			logger.error('Unable to post tweet', exc_info = ex)
	
	@models.permalink
	def get_absolute_url(self):
		return ('stream', [self.slug])
	
	class Meta:
		ordering = ('-updated',)
		get_latest_by = 'updated'
	
	class QuerySet(models.query.QuerySet):
		def public(self):
			return self.filter(
				pk__in = UserStream.objects.public().values_list('part_of__pk')
			).extra(
				where = (
					'(SELECT COUNT(*) FROM `%(Post)s` INNER JOIN ' \
					'`%(UserStream)s` ON `%(UserStream)s`.`id` = `%(Post)s`.`stream_id` WHERE ' \
					'`%(UserStream)s`.`private` = 0 AND `%(UserStream)s`.`part_of_id` = ' \
					'`%(Stream)s`.`id`) > 0' % {
						'Post': Post._meta.db_table,
						'UserStream': UserStream._meta.db_table,
						'Stream': Stream._meta.db_table
					},
				)
			)
		
		def summary(self):
			return self.extra(
				select = {
					'post_count': 'SELECT COUNT(*) FROM `%(Post)s` INNER JOIN ' \
						'`%(UserStream)s` ON `%(UserStream)s`.`id` = `%(Post)s`.`stream_id` WHERE ' \
						'`%(UserStream)s`.`private` = 0 AND `%(UserStream)s`.`part_of_id` = ' \
						'`%(Stream)s`.`id`' % {
							'Post': Post._meta.db_table,
							'UserStream': UserStream._meta.db_table,
							'Stream': Stream._meta.db_table
						},
					'contributor_count': 'SELECT COUNT(*) FROM `%(UserStream)s` WHERE ' \
						'`%(UserStream)s`.`private` = 0 AND `%(UserStream)s`.`part_of_id` = ' \
						'`%(Stream)s`.`id`' % {
							'UserStream': UserStream._meta.db_table,
							'Stream': Stream._meta.db_table
						}
				}
			)
		
		def near(self, latitude, longitude):
			sql = """(SELECT COUNT(*) FROM `%(Post)s` INNER JOIN `%(UserStream)s` ON
			`%(Post)s`.`stream_id` = `%(UserStream)s`.`id` WHERE ((ACOS(SIN(%(latitude)s * PI() /
			180) * SIN(`%(Post)s`.`latitude` * PI() / 180) + COS(%(latitude)s * PI() / 180) *
			COS(`%(Post)s`.`latitude` * PI() / 180) * COS((%(longitude)s - 
			`%(Post)s`.`longitude`) * PI() / 180)) * 180 / PI()) * 60 * 1.1515) <= 10 AND
			`%(UserStream)s`.`part_of_id` = `%(Stream)s`.`id`)""" % {
				'latitude': latitude,
				'longitude': longitude,
				'Post': Post._meta.db_table,
				'Stream': self.model._meta.db_table,
				'UserStream': UserStream._meta.db_table
			}
			
			qs = self.exclude(
				contributors__posts__latitude = '',
				contributors__posts__longitude = '',
				contributors__posts__latitude__isnull = True,
				contributors__posts__longitude__isnull = True
			).extra(
				where = [
					'%s <= 5' % sql
				]
			)
			
			return qs

class StreamTag(models.Model):
	stream = models.ForeignKey('Stream', related_name = 'tags')
	user = models.ForeignKey('auth.User', related_name = 'stream_tags', null = True)
	domain = models.CharField(max_length = 100)
	tag = models.CharField(max_length = 30)
	
	def __unicode__(self):
		return self.tag
	
	class Meta:
		db_table = 'streams_stream_tag'
		unique_together = ('stream', 'user', 'domain', 'tag')

class UserStream(models.Model):
	part_of = models.ForeignKey('Stream', related_name = 'contributors')
	private = models.BooleanField()
	profile = models.ForeignKey('auth.User', related_name = 'streams')
	updated = models.DateTimeField(auto_now_add = True, auto_now = True)
	objects = managers.UserStreamManager()
	
	def __unicode__(self):
		return unicode(self.part_of)
	
	def get_absolute_url(self):
		return self.part_of.get_absolute_url()
	
	def get_full_base_url(self):
		return 'http://%s.%s%s' % (
			self.profile.username,
			self.part_of.network.domain,
			self.get_absolute_url()
		)
	
	def get_embed_code(self):
		return self.part_of.get_embed_code(
			self.get_full_base_url()
		)
	
	def save(self, *args, **kwargs):
		super(UserStream, self).save(*args, **kwargs)
		self.part_of.updated = self.updated
		self.part_of.save()
	
	class QuerySet(models.query.QuerySet):
		def near(self, latitude, longitude):
			sql = """(SELECT COUNT(*) FROM `%(Post)s` WHERE ((ACOS(SIN(%(latitude)s * PI() /
			180) * SIN(`%(Post)s`.`latitude` * PI() / 180) + COS(%(latitude)s * PI() / 180) *
			COS(`%(Post)s`.`latitude` * PI() / 180) * COS((%(longitude)s - 
			`%(Post)s`.`longitude`) * PI() / 180)) * 180 / PI()) * 60 * 1.1515) <= 1 AND
			`%(Post)s`.`stream_id` = `%(UserStream)s`.`id`)""" % {
				'latitude': latitude,
				'longitude': longitude,
				'Post': Post._meta.db_table,
				'UserStream': self.model._meta.db_table
			}
			
			qs = self.exclude(
				posts__latitude = '',
				posts__longitude = '',
				posts__latitude__isnull = True,
				posts__longitude__isnull = True
			).extra(
				where = [
					'%s <= 5' % sql
				]
			)
			
			return qs
		
		def live(self):
			return self.filter(posts__state = 2)
			
		def public(self):
			return self.filter(private = False)
		
		def summary(self):
			return self.extra(
				select = {
					'post_count': 'SELECT COUNT(*) FROM `%(Post)s` WHERE ' \
						'`%(Post)s`.`stream_id` = `%(UserStream)s`.`id`'  % {
							'Post': Post._meta.db_table,
							'UserStream': UserStream._meta.db_table,
						}
				}
			)
	
	class Meta:
		db_table = 'streams_stream_user'
		ordering = ('-updated',)
		get_latest_by = 'updated'
		verbose_name = 'contributor'

class StreamEmbed(models.Model):
	stream = models.ForeignKey('UserStream', related_name = 'embeds')
	domain = models.CharField(max_length = 100)
	
	def __unicode__(self):
		return self.domain
	
	class Meta:
		db_table = 'streams_stream_embed'
		ordering = ('domain',)
		unique_together = ('stream', 'domain')

class Post(models.Model):
	stream = models.ForeignKey('UserStream', related_name = 'posts')
	posted = models.DateTimeField()
	kind = models.CharField(max_length = 10, choices = POST_TYPES)
	text = models.CharField(max_length = 200, null = True, blank = True)
	tags = TaggableManager()
	author = models.ForeignKey('auth.User', null = True, blank = True, related_name = 'posts')
	application = models.ForeignKey('piston.Consumer',
		null = True, blank = True, related_name = 'posts', editable = False
	)
	latitude = models.CharField(max_length = 30, null = True, blank = True)
	longitude = models.CharField(max_length = 30, null = True, blank = True)
	area = models.CharField(max_length = 50, null = True, blank = True)
	tweet = models.BooleanField()
	state = models.IntegerField(choices = POST_STATES, default = POST_LIVE)
	guid = models.CharField(max_length = 36, unique = True, null = True, blank = True)
	comments = generic.GenericRelation('social.Comment')
	objects = managers.PostManager()
	
	@property
	def html_template_name(self):
		return 'posts/%s.inc.html' % self.kind
	
	@property
	def js_template_name(self):
		return 'posts/%s.inc.js' % self.kind
	
	def __unicode__(self):
		return unicode(self.text)
	
	@models.permalink
	def get_absolute_url(self):
		return ('stream_post', [self.stream.part_of.slug, self.pk])
	
	def update_twitter(self):
		from django.conf import settings
		from meegloo.core.models import OAuthToken
		from meegloo.urlshortening.helpers import shorten
		from meegloo.social.helpers import format_tweet
		from twitter import Api
		
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
		
		tags = self.get_twitter_tags()
		tags = ['#%s' % t for t in self.tags.values_list('slug', flat = True)] + \
			['#%s' % t for t in tags]
		
		url = shorten(self, self.stream.part_of.network, self.author)
		tweet = format_tweet(self.text, tags, url)
		
		try:
			api.PostUpdate(tweet)
		except Exception, ex:
			logger.error('Unable to post tweet', exc_info = ex)
	
	def get_twitter_tags(self):
		return StreamTag.objects.filter(
			user = self.author,
			stream = self.stream.part_of,
			domain = 'twitter.com'
		).values_list('tag', flat = True)
	
	def clean(self):
		if self.kind == 'text' and not self.text:
			raise ValidationError('Text cannot be empty for this type of post')
	
	def is_question(self):
		for line in self.text.splitlines():
			if line.strip().endswith('?'):
				return True
		
		return False
	
	def convert_to_question(self):
		from django.contrib.contenttypes.models import ContentType
		from meegloo.social.models import Poll, Question
		import re
		
		prompt_line = -1
		lines = self.text.splitlines()
		li = re.compile(r'^(\d+)\. (.+)')
		options = []
		
		for (i, line) in enumerate(lines):
			if line.strip().endswith('?'):
				prompt_line = i
				prompt = line
		
		if prompt_line > -1:
			self.text = prompt
		
		is_poll = False
		if len(lines) > prompt_line + 1:
			# There may be a poll here
			
			for line in lines[prompt_line + 1:]:
				if line:
					matches = li.match(line)
					if matches:
						order, label = matches.groups()
						options.append(
							(order, label)
						)
						
						is_poll = True
					else:
						is_poll = False
						break
			
			if is_poll:
				self.kind = 'poll'
				super(Post, self).save()
				
				poll = Poll.objects.create(
					content_type = ContentType.objects.get_for_model(self),
					object_id = self.pk,
					prompt = prompt
				)
				
				for (order, label) in options:
					poll.options.create(
						order = order,
						label = label
					)
					
				return
		
		if prompt_line + 1 < len(lines):
			self.text = ' '.join(self.text.splitlines())
			super(Post, self).save()
			return
		
		self.kind = 'question'
		super(Post, self).save()
		
		Question.objects.create(
			content_type = ContentType.objects.get_for_model(self),
			object_id = self.pk,
			prompt = prompt
		)
		
	def convert_to_url(self):
		from django.utils.encoding import force_unicode
		from django.conf import settings
		from meegloo.oembed.helpers import match as oembed_match
		import re, string
		
		leading = ('(', '<', '[')
		trailing = ('.', ',', ')', '>', '\n', ']')
		words = re.compile(r'(\s+)')
		punctuation = re.compile('^(?P<lead>(?:%s)*)(?P<middle>.*?)(?P<trail>(?:%s)*)$' % \
		    ('|'.join([re.escape(x) for x in leading]),
		    '|'.join([re.escape(x) for x in trailing])))
		
		domain_suffixes = getattr(settings, 'DOMAIN_SUFFIXES', ())
		
		urls = []
		urls_lower = []
		
		for word in words.split(force_unicode(self.text)):
			match = None
			
			if '.' in word or '@' in word or ':' in word:
				match = punctuation.match(word)
			
			if match:
				lead, middle, trail = match.groups()
			else:
				continue
			
			url = None
			url_lower = None
			if middle.startswith('http://') or middle.startswith('https://'):
				url = middle
				url_lower = middle.lower()
			elif middle.startswith('www.') or (
				'@' not in middle and middle and middle[0] in string.ascii_letters + string.digits
			):
				lastdot = middle.rfind('.')
				if lastdot > -1:
					if middle[lastdot:] in domain_suffixes:
						url = 'http://%s' % middle
						url = url.lower()
			
			if url and not url_lower in urls_lower:
				urls.append(url)
				urls_lower.append(url_lower)
		
		if any(urls):
			self.kind = 'url'
			super(Post, self).save()
			i = 0
			
			for url in urls:
				if oembed_match(url):
					self.embeddables.create(
						url = url,
						order = i
					)
					
					i += 1
		else:
			super(Post, self).save()
	
	def save(self, *args, **kwargs):
		from datetime import datetime, timedelta
		from meegloo.uploadify.models import Upload
		
		logger = logging.getLogger()
		if not self.posted:
			self.posted = datetime.now()
		
		if not self.guid:
			from uuid import uuid4
			self.guid = str(uuid4())
		
		tags = kwargs.pop('tags', '')
		new = not self.pk
		
		if new:
			if self.latitude and self.longitude:
				self.area = helpers.reverse_geocode(self.latitude, self.longitude)
			
			self.stream.updated = self.posted
			self.stream.save()
			
			if Upload.objects.filter(guid = self.guid).count() == 0 and self.kind == 'text':
				if self.text and (self.text.find('http://') > -1 or self.text.find('https://') > -1):
					self.convert_to_url()
				elif self.is_question():
					self.convert_to_question()
				else:
					super(Post, self).save(*args, **kwargs)
			else:
				super(Post, self).save(*args, **kwargs)
			
			if tags:
				self.tags.add(*tags.split(' '))
		else:
			super(Post, self).save(*args, **kwargs)
		
		if new:
			from mimetypes import guess_type
			from django.conf import settings
			from django.core.files import File
			from os import path, remove
			
			for upload in Upload.objects.filter(guid = self.guid):
				mimetype, encoding = guess_type(upload.filename)
				recognised = False
				
				if mimetype:
					routes = getattr(settings, 'MIME_TYPE_ROUTES', ())
					for (route, types) in routes:
						if mimetype in types:
							self.kind = route
							self.state = POST_CONVERTING
							
							super(Post, self).save(*args, **kwargs)
							recognised = True
							logger.debug('Processing %s upload' % route)
							
							if self.kind in ('audio', 'video'):
								conversion = self.conversions.create(
									name = path.split(upload.filename)[-1],
									state = u'Started'
								)
								
								conversion.start(upload.filename)
							else:
								ff = File(f, name = path.split(upload.filename)[-1])
								self.media.create(
									mimetype = mimetype,
									content = ff
								)
								
								self.state = POST_LIVE
								super(Post, self).save(*args, **kwargs)
						
							break
					
				if not recognised:
					logger.error('Unrecognised MIME type %s' % mimetype)
					if path.exists(upload.filename):
						remove(upload.filename)
				
				upload.delete()
			
			next_set = self.stream.sets.filter(
				posted__gte = self.posted - timedelta(minutes = 1),
				kind = self.kind,
				application = self.application
			)
			
			if next_set.count() == 0:
				next_set = self.stream.sets.create(
					posted = self.posted,
					kind = self.kind,
					application = self.application
				)
			else:
				next_set = next_set.latest()
			
			next_set.posts.add(self)
			next_set.posted = self.posted
			next_set.save()
	
	class Meta:
		get_latest_by = 'posted'
		ordering = ('-posted',)
	
	class QuerySet(models.query.QuerySet):
		def live(self):
			return self.filter(state = POST_LIVE)
		
		def public(self):
			return self.filter(stream__private = False)

class Embeddable(models.Model):
	post = models.ForeignKey('Post', related_name = 'embeddables')
	url = models.URLField()
	order = models.PositiveIntegerField()
	
	@property
	def tag(self):
		return '%d_%d' % (self.post.pk, self.pk)
	
	def __unicode__(self):
		return self.url
	
	class Meta:
		unique_together = ('post', 'url')
		ordering = ('order',)

class Media(models.Model):
	post = models.ForeignKey('Post', related_name = 'media')
	mimetype = models.CharField(max_length = 100)
	content = models.FileField(upload_to = helpers.upload_post_media, null = True, blank = True)
	objects = managers.MediaManager()
	
	def __unicode__(self):
		return self.content.name
	
	class Meta:
		ordering = ('post', 'content')
		unique_together = ('post', 'mimetype')
		verbose_name = 'media item'
		verbose_name_plural = 'media'
	
	class QuerySet(models.query.QuerySet):
		def image(self):
			return self.get(mimetype__startswith = 'image/')
		
		def flv(self):
			return self.get(mimetype = 'video/x-flv')
		
		def mp3(self):
			return self.get(mimetype__in = ('audio/mp3', 'audio/mpeg'))
		
		def mp4(self):
			return self.get(mimetype = 'video/mp4')

class Set(models.Model):
	stream = models.ForeignKey('UserStream', related_name = 'sets')
	posted = models.DateTimeField()
	kind = models.CharField(max_length = 10, choices = POST_TYPES)
	text = models.CharField(max_length = 200, null = True, blank = True)
	posts = models.ManyToManyField('Post', related_name = 'sets')
	application = models.ForeignKey('piston.Consumer',
		null = True, blank = True, related_name = 'sets', editable = False
	)
	
	comments = generic.GenericRelation('social.Comment')
	
	@models.permalink
	def get_absolute_url(self):
		return ('stream_set', [self.stream.part_of.slug, self.pk])
	
	def get_twitter_tags(self):
		return StreamTag.objects.filter(
			user__username__in = self.posts.values_list('author__username', flat = True).distinct(),
			stream = self.stream.part_of,
			domain = 'twitter.com'
		).values_list('tag', flat = True).distinct()
	
	def __unicode__(self):
		return self.text or '%s set' % self.get_kind_display()
	
	def save(self, *args, **kwargs):
		if not self.posted:
			self.posted = self.posts.latest().posted
		
		if not self.pk:
			Stream.objects.filter(pk = self.stream.pk).update(
				updated = self.posted
			)
		
		super(Set, self).save(*args, **kwargs)
	
	class Meta:
		get_latest_by = 'posted'
		ordering = ('posted',)

class Conversion(models.Model):
	post = models.ForeignKey('Post', related_name = 'conversions')
	updated = models.DateTimeField(auto_now = True)
	name = models.CharField(max_length = 255)
	state = models.CharField(max_length = 255)
	state_description = models.TextField(null = True, blank = True)
	
	def __unicode__(self):
		return self.name
	
	def start(self, filename):
		if not self.pk:
			self.save()
		
		from django.utils.importlib import import_module
		converter = import_module('meegloo.streams.conversion.%s' % self.post.kind)
		converter.convert(filename, self.pk)
	
	class Meta:
		get_latest_by = 'updated'
		ordering = ('updated',)

class Trend(models.Model):
	stream = models.ForeignKey(Stream, related_name = 'trends')
	time = models.DateTimeField(auto_now_add = True)
	posts = models.PositiveIntegerField(default = 0)
	objects = managers.TrendManager()
	
	def __unicode__(self):
		return unicode(self.stream)
	
	class QuerySet(models.query.QuerySet):
		def rebuild(self):
			from datetime import datetime, timedelta
			from django.db.models import Count
			from meegloo.networks.models import Network
			
			for network in Network.objects.all():
				today = datetime.now().date()
				last_week = today - timedelta(days = 7)
				self.filter(
					stream__network = network,
					time__lte = last_week
				).delete()
				
				updated = Stream.objects.filter(network = network).public()
				
				if self.filter(stream__network = network).count() > 0:
					updated = updated.filter(
						updated__gte = self.latest().time
					)
				else:
					updated = updated.filter(
						updated__gte = last_week
					)
				
				updated = updated.annotate(
					post_count = Count('contributors__posts')
				).filter(
					post_count__gt = 0
				).order_by('-post_count')[:10]
				
				for stream in updated:
					if self.filter(stream = stream).count() > 0:
						self.filter(stream = stream).update(
							posts = stream.post_count
						)
					else:
						self.create(
							stream = stream,
							posts = stream.post_count
						)
	
	class Meta:
		ordering = ('-time', '-posts')
		get_latest_by = 'time'

from meegloo.streams.conversion.audio import *
from meegloo.streams.conversion.video import *
from django.db.models import signals as db

db.post_save.connect(helpers.post_save, sender = Post)