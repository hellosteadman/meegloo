#!/usr/bin/env python
# encoding: utf-8

from piston.authentication import initialize_server_request, send_oauth_error
from piston.oauth import OAuthError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.conf import settings
from meegloo.api.helpers import format_errors
from meegloo.streams.models import Post, Media
from meegloo.networks.models import Network
from meegloo.registration.forms import RegistrationForm
from sorl.thumbnail import get_thumbnail
from urllib import urlopen, urlencode
from hashlib import md5

@csrf_exempt
def oauth_user_auth(request):
	oauth_server, oauth_request = initialize_server_request(request)
	
	if oauth_request is None:
		return send_oauth_error(
			OAuthError('Invalid request parameters.')
		)
	
	try:
		token = oauth_server.fetch_request_token(oauth_request)
		if not token.consumer.user.is_superuser:
			raise OAuthError('Method only allowed for approved applications.')
	except OAuthError, err:
		return send_oauth_error(err)
	
	if request.method == 'POST':
		form = AuthenticationForm(data = request.POST)
		
		if form.is_valid():
			request.user = form.get_user()
			token = oauth_server.authorize_token(token, request.user)
			return HttpResponse(token.to_string())
		
		return send_oauth_error(
			OAuthError('Invalid username or password')
		)
	
	return send_oauth_error(OAuthError('Invalid action.'))

@csrf_exempt
def oauth_register(request):
	oauth_server, oauth_request = initialize_server_request(request)
	
	if oauth_request is None:
		return send_oauth_error(
			OAuthError('Invalid request parameters.')
		)
	
	try:
		token = oauth_server.fetch_request_token(oauth_request)
		if not token.consumer.user.is_superuser:
			raise OAuthError('Method only allowed for approved applications.')
	except OAuthError, err:
		return send_oauth_error(err)
	
	if request.method == 'POST':
		form = RegistrationForm(data = request.POST)
		
		if form.is_valid():
			request.user = form.save()
			token = oauth_server.authorize_token(token, request.user)
			return HttpResponse(token.to_string())
		
		return send_oauth_error(
			OAuthError(
				format_errors(form.errors)
			)
		)
	
	return send_oauth_error(OAuthError('Invalid action.'))

@cache_page(60)
def post_thumbnail(request, stream, id, size = '560x560'):
	post = get_object_or_404(
		Post,
		stream__part_of__slug = stream,
		stream__part_of__network__parent = request.network.parent,
		pk = id
	)
	
	try:
		img = post.media.image()
	except Media.DoesNotExist:
		raise Http404()
	
	media_url = getattr(settings, 'MEDIA_URL')
	img = get_thumbnail(img.content, size, crop = 'center', quality = 99)
	url = img.url
	q = url.find('?')
	
	if q > 01:
		url = url[:q]
	
	return HttpResponseRedirect(url)

@cache_page(60 * 60)
def network_icon(request, id, size = '50x50'):
	post = get_object_or_404(
		Network, parent = request.network.parent, pk = id, icon__isnull = False
	)
	
	if post.icon:
		media_url = getattr(settings, 'MEDIA_URL')
		img = get_thumbnail(post.icon, size, crop = 'center', quality = 99)
		url = img.url
		q = url.find('?')
		
		if q > 01:
			url = url[:q]
		
		return HttpResponseRedirect(url)
	
	raise Http404()

@cache_page(60 * 60 * 3)
def user_avatar(request, username, size = '50'):
	user = get_object_or_404(User, username__iexact = username)
	media_url = getattr(settings, 'MEDIA_URL')
	
	try:
		size = int(size)
	except (ValueError, TypeError):
		size = 50
	
	img = urlopen(
		'http://www.gravatar.com/avatar/%s.png?%s' % (
			md5(user.email.lower()).hexdigest(),
			urlencode(
				{
					'd': '%simg/avatar.png' % media_url,
					's': size
				}
			)
		)
	)
	
	return HttpResponse(img.read(), 'image/png')

@cache_page(60)
def post(request, stream, id):
	post = get_object_or_404(
		Post, stream__part_of__slug = stream, pk = id
	)
	
	return TemplateResponse(
		request,
		'api/post.html',
		{
			'post': post
		}
	)

def comments(request, stream, id):
	post = get_object_or_404(
		Post, stream__part_of__slug = stream, pk = id
	)

	return TemplateResponse(
		request,
		'api/comments.html',
		{
			'comments': post.comments.all()[:10]
		}
	)