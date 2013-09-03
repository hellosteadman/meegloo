#!/usr/bin/env python
# encoding: utf-8

from django.db import models
from django.conf import settings
from meegloo.core import helpers, managers
import logging

class Profile(models.Model):
	user = models.ForeignKey('auth.User', related_name = 'profiles')
	embed_key = models.CharField(max_length = 20, unique = True)
	embed_key_hashed = models.CharField(max_length = 64, unique = True)	
	avatar = models.ImageField(upload_to = helpers.upload_avatar, null = True, blank = True)
	
	def __unicode__(self):
		return self.user.get_full_name() or self.user.username
	
	def save(self, *args, **kwargs):
		if not self.embed_key:
			import random, string
			
			key = ''.join(random.sample(string.digits + string.letters, 20))
			while Profile.objects.filter(embed_key = key).count() > 0:
				key = ''.join(random.sample(string.digits + string.letters, 20))
			
			self.embed_key = key
		
		if not self.embed_key_hashed:
			from hashlib import md5
			self.embed_key_hashed = md5(self.embed_key).hexdigest()
		
		super(Profile, self).save(*args, **kwargs)

class OAuthToken(models.Model):
	user = models.ForeignKey('auth.User', related_name = 'oauth_tokens')
	site = models.CharField(max_length = 20)
	token = models.CharField(max_length = 200)
	secret = models.CharField(max_length = 200)
	username = models.CharField(max_length = 50, null = True, blank = True)
	objects = managers.OAuthTokenManager()
	
	def __unicode__(self):
		return self.site
	
	def update_username(self):
		logger = logging.getLogger()
		if self.site == 'twitter':
			from twitter import Api
			
			oauth_creds = getattr(settings, 'OAUTH_CREDENTIALS').get('TWITTER')
			api = Api(
				consumer_key = oauth_creds.get('CONSUMER_KEY'),
				consumer_secret = oauth_creds.get('CONSUMER_SECRET'),
				access_token_key = self.token,
				access_token_secret = self.secret
			)
			
			try:
				user = api.VerifyCredentials()
				self.username = user.screen_name.lower()
			except Exception, ex:
				logger.error('Error getting Twitter screen name', exc_info = ex)
		
		elif self.site == 'flickr':
			from urllib import urlopen
			from oauth.oauth import OAuthToken, OAuthConsumer, OAuthRequest, OAuthSignatureMethod_HMAC_SHA1
			from httplib import HTTPSConnection,  HTTPConnection
			from elementtree import ElementTree
			
			oauth_creds = getattr(settings, 'OAUTH_CREDENTIALS').get('FLICKR')
			api_url = 'http://api.flickr.com/services/rest/'
			ssl = oauth_creds.get('SSL', False)
			server = oauth_creds.get('SERVER')
			klass = ssl and HTTPSConnection or HTTPConnection
			
			token = OAuthToken(
				str(self.token),
				str(self.secret)
			)
			
			consumer = OAuthConsumer(
				str(oauth_creds.get('CONSUMER_KEY')),
				str(oauth_creds.get('CONSUMER_SECRET'))
			)
			
			oauth_request = OAuthRequest.from_consumer_and_token(
				consumer, token = token,
				http_url = api_url, parameters = {
					'api_key': oauth_creds.get('CONSUMER_KEY'),
					'method': 'flickr.urls.getUserProfile'
				}
			)
			
			oauth_request.sign_request(OAuthSignatureMethod_HMAC_SHA1(), consumer, token)
			
			connection = klass(server)
			connection.request(oauth_request.http_method, oauth_request.to_url())
			resp = ElementTree.parse(
				connection.getresponse()
			)
			
			user = resp.find('user')
			if not user is None:
				self.username = user.get('nsid')
			else:
				logger.error('Unrecognised response',
					extra = {
						'data': {
							'response': [t.tag for t in resp.getchildren()]
						}
					}
				)
		elif self.site == 'facebook':
			from django.utils import simplejson
			from urllib import urlopen
			
			resp = simplejson.load(
				urlopen('https://graph.facebook.com/me/?access_token=%s' % self.token)
			)
			
			self.username = resp.get('username', resp.get('id')).lower()
		else:
			logger.error('OAuth credentials not found for %s', self.site)
	
	def get_user_url(self):
		if self.site == 'twitter':
			return 'http://twitter.com/%s/' % self.username
		elif self.site == 'flickr':
			return 'http://flickr.com/photos/%s/' % self.username
		elif self.site == 'facebook':
			return 'http://facebook.com/%s/' % self.username
		
	def save(self, *args, **kwargs):
		if not self.username:
			self.update_username()
		
		super(OAuthToken, self).save(*args, **kwargs)
	
	class Meta:
		unique_together = ('user', 'site')
		db_table = 'core_oauth'
		verbose_name = 'OAuth token'
	
	class QuerySet(models.query.QuerySet):
		def with_usernames(self):
			return self.filter(username__isnull = False)

class OAuthInvitation(models.Model):
	sender = models.ForeignKey('auth.User', related_name = 'oauth_invitations')
	site = models.CharField(max_length = 20)
	username_or_id = models.CharField(max_length = 50)
	invited = models.DateTimeField(auto_now_add = True)
	
	def __unicode__(self):
		return self.email
	
	class Meta:
		unique_together = ('sender', 'site', 'username_or_id')
		ordering = ('-invited',)
		db_table = 'core_invitation'