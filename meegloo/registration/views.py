#!/usr/bin/env python
# encoding: utf-8

from django.template.response import TemplateResponse
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from meegloo.core.models import OAuthToken, Profile
from meegloo.registration.forms import RegistrationForm, ProfileForm, ForgottenPasswordForm, PasswordResetForm
from meegloo.registration.models import EmailConfirmation, PasswordReset
from datetime import datetime

def register(request):
	if request.GET.get('username'):
		from django.contrib.auth.models import User
		
		if User.objects.filter(username__iexact = request.GET['username']).count() > 0:
			return HttpResponseRedirect(
				'http://%s.%s' % (
					request.GET['username'].lower(),
					request.network.domain
				)
			)
		
		initial = {
			'username': request.GET['username']
		}
	else:
		initial = {}
	
	form = RegistrationForm(
		data = request.POST or None,
		prefix = 'signup', initial = initial
	)
	
	if request.method == 'POST' and form.is_valid():
		user = form.save()
		user.email_confirmations.create(
			network = request.network
		)
		
		messages.add_message(
			request,
			messages.SUCCESS,
			_('Thanks for signing up. Welcome aboard!')
		)
		
		return HttpResponseRedirect('confirm/')
	
	return TemplateResponse(
		request,
		'registration/signup.html',
		{
			'form': form,
			'title_parts': (u'Signup for an account',)
		}
	)

def confirm_email(request):
	guid = request.GET.get('guid')
	
	try:
		confirmation = EmailConfirmation.objects.get(
			network__parent = request.network.parent,
			guid = guid
		)
		
		confirmation.confirm()
		
		messages.add_message(
			request,
			messages.SUCCESS,
			_('thanks for confirming your email address')
		)
		
		return HttpResponseRedirect(
			reverse('login')
		)
	
	except EmailConfirmation.DoesNotExist:
		return TemplateResponse(
			request,
			'registration/confirm-fail.html',
			{
				'title_parts': (u'Confirm your email address',)
			}
		)
		
def profile(request):
	if not request.profile:
		raise Http404()
	
	if Profile.objects.filter(user = request.profile).count() == 0:
		Profile.objects.create(user = request.profile)
	
	posts = request.profile.posts.filter(
		stream__private = False
	)[:10]
	
	paginator = Paginator(posts, 10)
	
	try:
		posts = paginator.page(1)
	except:
		posts = None
	
	return TemplateResponse(
		request,
		(
			'registration/profile.html'
		),
		{
			'posts': posts
		}
	)

@login_required
def edit_profile(request):
	form = ProfileForm(
		network = request.network,
		data = request.POST or None,
		files = request.FILES or None,
		instance = request.user
	)
	
	if not request.profile or request.profile.pk != request.user.pk:
		return HttpResponseRedirect(
			'http://%s.%s%s' % (
				request.user.username,
				request.network.domain,
				reverse('edit_profile')
			)
		)
		
	if request.network.is_external:
		return HttpResponseRedirect(
			'http://%s.meegloo.com%s' % (
				request.user.username,
				reverse('edit_profile')
			)
		)
	
	if request.method == 'POST' and form.is_valid():
		form.save()
		
		messages.add_message(
			request,
			messages.SUCCESS,
			u'Your profile has been updated'
		)
		
		return HttpResponseRedirect('/')
	
	if Profile.objects.filter(user = request.user).count() == 0:
		Profile.objects.create(user = request.user)
	
	connections = []
	
	for site, creds in getattr(settings, 'OAUTH_CREDENTIALS', {}).items():
		info = {
			'verbose_name': creds.get('VERBOSE_NAME', site.capitalize()),
			'site': site.lower(),
			'friendships': creds.get('FRIENDSHIPS', True)
		}
		
		try:
			token = request.user.oauth_tokens.get(site__iexact = site)
			info['connected'] = True
			info['url'] = reverse('oauth_unauth', args = [site.lower()])
		except OAuthToken.DoesNotExist:
			info['connected'] = False
			info['url'] = reverse('oauth_auth', args = [site.lower()])
		
		connections.append(info)
	
	return TemplateResponse(
		request,
		'registration/edit.html',
		{
			'form': form,
			'title_parts': (u'Edit your profile',),
			'connections': connections
		}
	)

def forgot_password(request):
	if request.user.is_authenticated():
		messages.add_message(
			request,
			messages.WARNING,
			u'You are already logged in.'
		)
		
		return HttpResponseRedirect(
			reverse('edit_profile')
		)
	
	form = ForgottenPasswordForm(
		network = request.network,
		data = request.POST or None
	)
	
	if request.method == 'POST' and form.is_valid():
		form.save()
		return TemplateResponse(
			request,
			'registration/reset-done.html',
			{
				'title_parts': (u'Forgotten password',)
			}
		)
		
	return TemplateResponse(
		request,
		'registration/reset-form.html',
		{
			'form': form,
			'state': 1,
			'title_parts': (u'Forgotten password',)
		}
	)

def reset_password(request):
	if request.user.is_authenticated():
		messages.add_message(
			request,
			messages.WARNING,
			u'You are already logged in.'
		)
		
		return HttpResponseRedirect(
			reverse('edit_profile')
		)
	
	guid = request.GET.get('guid')
	
	try:
		reset = PasswordReset.objects.get(
			network__parent = request.network.parent,
			guid = guid,
			expires__gte = datetime.now()
		)
	except PasswordReset.DoesNotExist:
		return TemplateResponse(
			request,
			'registration/reset-fail.html',
			{
				'title_parts': (u'Reset password',)
			}
		)
	
	form = PasswordResetForm(
		reset = reset,
		data = request.POST or None
	)
	
	if request.method == 'POST' and form.is_valid():
		form.save()
		
		messages.add_message(
			request,
			messages.SUCCESS,
			u'Your password has been reset successfully.'
		)
		
		PasswordReset.objects.filter(
			expires__lte = datetime.now()
		).delete()
		
		return HttpResponseRedirect(
			reverse('login')
		)
			
	return TemplateResponse(
		request,
		'registration/reset-form.html',
		{
			'form': form,
			'state': 2,
			'title_parts': (u'Forgotten password',)
		}
	)