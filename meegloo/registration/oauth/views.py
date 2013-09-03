#!/usr/bin/env python
# encoding: utf-8

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from oauth.oauth import OAuthConsumer, OAuthRequest, OAuthToken, OAuthSignatureMethod_HMAC_SHA1
from httplib import HTTPConnection, HTTPSConnection
from meegloo.core import models as core
from urllib import urlopen

OAUTH_CREDENTIALS = getattr(settings, 'OAUTH_CREDENTIALS')
SIGNATURE_METHOD = OAuthSignatureMethod_HMAC_SHA1

@login_required
def unauth(request, site):
	creds = OAUTH_CREDENTIALS.get(site.upper())
	if not creds:
		raise Http404('Site %s not found' % site)
	
	request.user.oauth_tokens.filter(site__iexact = site).delete()
	messages.add_message(
		request,
		messages.SUCCESS,
		u'You have been successfully disconnected from %s.' % creds.get(
			'VERBOSE_NAME', site.capitalize()
		)
	)
	
	return HttpResponseRedirect(
		request.META.get('HTTP_REFERER', '/')
	)

@login_required
def auth(request, site):
	creds = OAUTH_CREDENTIALS.get(site.upper())
	if not creds:
		raise Http404('Site %s not found' % site)
	
	urls = creds.get('URLS', {})
	
	if 'DIALOG' in urls:
		request.session['preauth_url'] = request.META.get('HTTP_REFERER')
		return HttpResponseRedirect(urls['DIALOG'])
	
	ssl = creds.get('SSL', False)
	server = creds.get('SERVER', '%s.com' % site.lower())
	klass = ssl and HTTPSConnection or HTTPConnection
	
	request.session['preauth_url'] = request.META.get('HTTP_REFERER')
	
	consumer = OAuthConsumer(
		str(creds['CONSUMER_KEY']),
		str(creds['CONSUMER_SECRET'])
	)
	
	oauth_request = OAuthRequest.from_consumer_and_token(
		consumer, http_url = urls.get('REQUEST_TOKEN')
	)
	
	oauth_request.sign_request(SIGNATURE_METHOD(), consumer, None)
	url = oauth_request.to_url()
	
	connection = klass(server)
	connection.request(oauth_request.http_method, url)
	response = connection.getresponse()
	resp = response.read()
	
	token = OAuthToken.from_string(resp)
	request.session['unauth_token'] = token
	
	auth_url = urls.get('AUTHORISATION')
	if isinstance(auth_url, (list, tuple)):
		params = auth_url[1]
		auth_url = auth_url[0]
	else:
		params = {}
	
	oauth_request = OAuthRequest.from_consumer_and_token(
		consumer, token = token,
		http_url = auth_url, parameters = params
	)
	
	oauth_request.sign_request(SIGNATURE_METHOD(), consumer, token)
	return HttpResponseRedirect(
		oauth_request.to_url()
	)

def return_auth(request, site):
	creds = OAUTH_CREDENTIALS.get(site.upper())
	if not creds:
		raise Http404('Site %s not found' % site)
	
	urls = creds.get('URLS', {})
	ssl = creds.get('SSL', False)
	server = creds.get('SERVER', '%s.com' % site.lower())
	
	if not 'DIALOG' in urls:
		token = request.session.get('unauth_token')
		if not token:
			return HttpResponse('No unauthorised token')
	
		if token.key != request.GET.get('oauth_token', None):
			if request.session.get('preauth_url'):
				return HttpResponseRedirect(
					request.session['preauth_url']
				)
			else:
				return HttpResponse('')
	
		verifier = request.GET.get('oauth_verifier')
		consumer = OAuthConsumer(
			str(creds.get('CONSUMER_KEY')),
			str(creds.get('CONSUMER_SECRET'))
		)

		oauth_request = OAuthRequest.from_consumer_and_token(
			consumer, token = token,
			http_url = urls.get('ACCESS_TOKEN'),
			parameters = {
				'oauth_verifier': verifier
			}
		)

		oauth_request.sign_request(SIGNATURE_METHOD(), consumer, token)
		url = oauth_request.to_url()
		
		access_token = OAuthToken.from_string(
			urlopen(url).read()
		)
		
		if request.user.is_authenticated():
			try:
				token = request.user.oauth_tokens.get(
					site = site
				)
				
				token.token = access_token.key
				token.secret = access_token.secret
				token.save()
			except core.OAuthToken.DoesNotExist:
				request.user.oauth_tokens.create(
					site = site,
					token = access_token.key,
					secret = access_token.secret
				)
		else:
			return HttpResponse('')
	else:
		url = urls.get('ACCESS_TOKEN') % request.GET.get('code')
		resp = urlopen(url).read()
		d = {}
		
		for (key, value) in [i.split('=') for i in resp.split('&')]:
			if key:
				d[key] = value
		
		if request.user.is_authenticated():
			try:
				token = request.user.oauth_tokens.get(
					site = site
				)
				
				token.token = d['access_token']
				token.save()
			except core.OAuthToken.DoesNotExist:
				request.user.oauth_tokens.create(
					site = site,
					token = d['access_token']
				)
		else:
			return HttpResponse('')
	
	if request.session.get('preauth_url'):
		messages.add_message(
			request,
			messages.SUCCESS,
			u'You have been successfully connected to %s.' % creds.get(
				'VERBOSE_NAME', site.capitalize()
			)
		)
		
		return HttpResponseRedirect(
			request.session['preauth_url']
		)
	else:
		return HttpResponse('')

@login_required
def connect(request, site):
	creds = OAUTH_CREDENTIALS.get(site.upper())
	if not creds:
		raise Http404('Site %s not found' % site)
	
	if not creds.get('FRIENDSHIPS', True):
		raise Http404('Friendships not implemented')
	
	if request.user.oauth_tokens.filter(site = site).count() == 0:
		return HttpResponseRedirect(
			reverse('oauth_auth', args = [site])
		)
	
	return TemplateResponse(
		request,
		'oauth/connect.html',
		{
			'site': creds,
			'site_key': site,
			'body_classes': ('connect', 'cnnect-%s' % site)
		}
	)

@login_required
@csrf_exempt
def connect_json(request, site):
	creds = OAUTH_CREDENTIALS.get(site.upper())
	if not creds:
		raise Http404('Site %s not found' % site)
	
	if not creds.get('FRIENDSHIPS', True):
		raise Http404('Friendships not implemented')
	
	if request.user.oauth_tokens.filter(site = site).count() == 0:
		raise Http404('User not connected to %s' % site)
	
	if request.method == 'GET':
		page = 1
		if request.GET.get('page'):
			try:
				page = int(request.GET.get('page'))
			except:
				pass
		
		token = request.user.oauth_tokens.get(site = site)
		connections = core.OAuthToken.objects.filter(
			site = site
		).values_list('username', flat = True).distinct()
		
		connections = [u.lower() for u in connections]
		
		friends = []
		followers = core.OAuthToken.objects.filter(
			site = site,
			user__pk__in = request.user.following.values_list('followee__pk', flat = True)
		).values_list('username', flat = True)
		
		if site == 'twitter':
			from twitter import Api
			
			api = Api(
				consumer_key = creds.get('CONSUMER_KEY'),
				consumer_secret = creds.get('CONSUMER_SECRET'),
				access_token_key = token.token,
				access_token_secret = token.secret
			)
			
			for user in api.GetFriends():
				if user.screen_name.lower() in connections:
					friends.append(
						{
							'username': user.screen_name.lower(),
							'full_name': user.name,
							'image': user.profile_image_url,
							'following': user.screen_name.lower() in followers,
							'show_username': True
						}
					)
		elif site == 'facebook':
			def add_friends():
				for user in result['data']:
					username_or_id = user.get('username', user.get('id'))
					
					if username_or_id in connections:
						friends.append(
							{
								'username': username_or_id,
								'full_name': user.get('name'),
								'following': user.get('id') in followers,
								'image': 'https://graph.facebook.com/%s/picture' % username_or_id,
								'show_username': False
							}
						)
			
			result = simplejson.load(
				urlopen('https://graph.facebook.com/me/friends/?access_token=%s&fields=id,username,name' % token.token)
			)
			
			if not 'data' in result:
				if 'error' in result and result['error'].get('type') == 'OAuthException':
					return HttpResponseRedirect(
						reverse('oauth_auth', args = [site])
					)
				
				raise Exception(result)
			
			add_friends()
			
			while result.get('paging', {}).get('next'):
				print 'Moving to next page'
				result = simplejson.load(
					urlopen(result['paging']['next'])
				)
				
				add_friends()
		
		return HttpResponse(
			simplejson.dumps(friends),
			mimetype = 'application/json'
		)
	elif request.method == 'POST':
		username_or_id = request.POST.get('id', request.POST.get('username')).lower()
		token = core.OAuthToken.objects.get(username = username_or_id, site = site)
		
		follow, created = request.user.following.get_or_create(
			followee = token.user
		)
		
		if created:
			follow.notify(request.network)
		
		return HttpResponse('OK', mimetype = 'text/plain')