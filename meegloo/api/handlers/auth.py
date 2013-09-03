#!/usr/bin/env python
# encoding: utf-8

from django.http import HttpResponseBadRequest
from django.conf import settings
from django.db.models import Count, Q
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from piston.utils import rc
from piston.handler import BaseHandler
from meegloo.core.models import OAuthToken
from meegloo.social.models import Follow

class UserHandler(BaseHandler):
	allowed_methods = ('GET',)
	model = User
	fields = ('first_name', 'last_name', 'date_joined', 'username')
	
	def read(self, request, username = None):
		if username:
			user = get_object_or_404(User, username = username)
		else:
			user = request.user
		
		d = {
			'first_name': user.first_name,
			'last_name': user.last_name,
			'joined': user.date_joined,
			'username': user.username,
			'followers': user.followers.count(),
			'following': user.following.count(),
			'posts': user.posts.count(),
			'streams': [
				{
					'id': pk,
					'slug': slug,
					'name': name,
					'category': category,
					'network': network,
				} for (pk, slug, name, category, network) in
				user.streams.public().filter(
					part_of__network = request.network
				).values_list(
					'part_of__pk', 'part_of__slug', 'part_of__name',
					'part_of__category__name', 'part_of__network__domain'
				)
			]
		}
		
		if user.pk != request.user.pk:
			d['am_following'] = request.user.following.filter(followee = user).count() > 0
		
		return d
		

class UserSearchHandler(BaseHandler):
	allowed_methods = ('GET',)
	
	def read(self, request):
		criteria = request.GET.get('q')
		
		if not criteria:
			return []
		
		words = criteria.split(' ')
		q = Q()
		
		for word in words:
			q |= Q(first_name__icontains = word) | Q(last_name__icontains = word) | Q(username__icontains = word)
		
		return [
			{
				'first_name': user.first_name,
				'last_name': user.last_name,
				'username': user.username,
			} for user in User.objects.filter(q)
		]
		
class OAuthTokenHandler(BaseHandler):
	model = OAuthToken
	exclude = ('secret', 'user', 'id')
	
	def create(self, request):
		site = request.POST.get('site')
		token = request.POST.get('token')
		secret = request.POST.get('secret')
		
		if not site:
			return HttpResponseBadRequest('site is required')
		
		if not 'token' in request.POST or not 'secret' in request.POST:
			return HttpResponseBadRequest('token and secret are required')
		
		if not token:
			request.user.oauth_tokens.filter(site__iexact = site).delete()
			return []
		else:
			try:
				obj = request.user.oauth_tokens.get(site__iexact = site)
				obj.token = token
				obj.secret = secret
				obj.save()
			except OAuthToken.DoesNotExist:
				obj = request.user.oauth_tokens.create(
					site = site,
					token = token,
					secret = secret
				)
		
			return obj
	
class CheckUsernameHandler(BaseHandler):
	"""
	Returns True if the username specified in the ``username`` argument is not already in use.
	"""
	
	allowed_methods = ('GET',)
	
	def read(self, request):
		username = request.GET.get('username')
		
		if not username:
			return HttpResponseBadRequest('No username supplied')
		
		username = username.lower()
		check = User.objects.filter(username = username).count() == 0
		
		if check:
			check = not username in getattr(settings, 'INVALID_USERNAMES', [])
		
		return check

class FollowerHandler(BaseHandler):
	allowed_methods = ('GET',)
	
	def read(self, request, username = None):
		if username:
			user = get_object_or_404(User, username = username)
		else:
			user = request.user
		
		return user.followers.all()
		
class FollowingHandler(BaseHandler):
	def read(self, request, username = None):
		if username:
			user = get_object_or_404(User, username = username)
		else:
			user = request.user
			
		return [
			{
				'username': username,
				'first_name': first_name,
				'last_name': last_name
			}
			
			for (username, first_name, last_name) in user.following.all().values_list(
				'followee__username', 'followee__first_name', 'followee__last_name'
			)
		]
	
	def create(self, request):
		try:
			followee = User.objects.get(username = request.POST.get('followee'))
		except:
			return HttpResponseBadRequest('followee is invalid')
		
		if request.user.following.filter(followee = followee).count() > 0:
			return HttpResponseBadRequest('You are already following %s' % followee.username)
		
		follow = request.user.following.create(
			followee = followee
		)
		
		follow.notify(request.network)
		return follow
	
	def delete(self, request, followee):
		followee = get_object_or_404(Follow, follower = request.user, followee__username = followee)
		followee.delete()
		
		return rc.DELETED