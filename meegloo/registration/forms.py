#!/usr/bin/env python
# encoding: utf-8

from django import forms
from django.core.validators import email_re
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.conf import settings
from meegloo.core.models import Profile
from meegloo.registration.widgets import RemovableImageFormField
import re

class RegistrationForm(forms.ModelForm):
	username = forms.RegexField(
		regex = r'^[\w]+$', max_length = 30,
		label = _('Choose a username'),
		help_text = _(
			'It\'ll form part of the address for all ' \
			'your streams (ie: http://johndoe.meegloo.com)'
		), error_messages = {
			'invalid': u'Your username should just contain letters and numbers'
		}
	)
	
	password = forms.CharField(
		label = _('Pick a password'), min_length = 7, max_length = 20,
		widget = forms.PasswordInput,
		help_text = _('Choose something between 7 and 20 characters')
	)
	
	email = forms.EmailField(
		label = _('And finally your email address'),
		help_text = _(
			'We might email you to let you know about Meegloo stuff, but ' \
			'of course we won\'t share it'
		)
	)
	
	def clean_username(self):
		username = self.cleaned_data.get('username')
		
		if username.lower() in getattr(settings, 'INVALID_USERNAMES', []):
			raise forms.ValidationError('Sorry, that isn\'t a valid username')
		
		if User.objects.filter(username__iexact = username).count() > 0:
			raise forms.ValidationError('Sorry, someone already has that username')
		
		from meegloo.networks.models import Network
		if Network.objects.filter(domain__startswith = '%s.' % username).count() > 0:
			raise forms.ValidationError('Sorry, that username isn\'t available')
		
		return username
	
	def clean_email(self):
		email = self.cleaned_data.get('email')

		if User.objects.filter(email__iexact = email).count() > 0:
			raise forms.ValidationError('That email address is already registered')

		return email
	
	def save(self):
		return User.objects.create_user(
			username = self.cleaned_data['username'],
			password = self.cleaned_data['password'],
			email = self.cleaned_data['email']
		)
	
	class Meta:
		model = User
		fields = ('username', 'password', 'email')

class ProfileForm(forms.ModelForm):
	username = forms.RegexField(
		regex = r'^[\w]+$', max_length = 30,
		label = _('Change your username'),
		help_text = _(
			u'Remember that this will change your Meegloo address (ie: http://johndoe.meegloo.com)'
		), error_messages = {
			'invalid': u'Your username should just contain letters and numbers'
		}
	)
	
	change_email = forms.EmailField(
		label = _('Change your email address'),
		help_text = _(
			'Make sure your inbox is setup, as we\'ll need to confirm the change of address'
		)
	)
	
	avatar = RemovableImageFormField(
		label = _('Upload an avatar'),
		help_text = _('If you don\'t specify one, we\'ll use your Gravatar')
	)
	
	password1 = forms.CharField(
		label = _('Change your password'), min_length = 7, max_length = 20,
		widget = forms.PasswordInput, required = False,
		help_text = _('Choose something between 7 and 20 characters')
	)
	
	password2 = forms.CharField(
		label = _('Confirm your new password'), min_length = 7, max_length = 20,
		widget = forms.PasswordInput, required = False,
		help_text = _('Just to be on the safe side')
	)
	
	def __init__(self, network, *args, **kwargs):
		super(ProfileForm, self).__init__(*args, **kwargs)
		self.network = network
		
		self.fields['change_email'].initial = self.instance.email
		self.fields['first_name'].help_text = u'This is how your name will appear in various ' \
			'sections of the site'
		
		self.fields['last_name'].help_text = u'If we were schoolmasters, this is how we would ' \
			'address you'
		
		if self.instance:
			try:
				profile = self.instance.get_profile()
				if profile.avatar:
					self.fields['avatar'].label = u'Change your avatar'
					self.fields['avatar'].initial = profile.avatar
			except Profile.DoesNotExist:
				pass
	
	def clean_username(self):
		username = self.cleaned_data.get('username')
		
		if username.lower() in getattr(settings, 'INVALID_USERNAMES', []):
			raise forms.ValidationError('Sorry, that isn\'t a valid username')
		
		if User.objects.filter(username__iexact = username).exclude(pk = self.instance.pk).count() > 0:
			raise forms.ValidationError('Sorry, someone already has that username')
		
		from meegloo.networks.models import Network
		if Network.objects.filter(domain__startswith = '%s.' % username).count() > 0:
			raise forms.ValidationError('Sorry, that username isn\'t available')
		
		return username
	
	def clean_email(self):
		email = self.cleaned_data.get('email')

		if User.objects.filter(email__iexact = email).exclude(pk = self.instance.pk).count() > 0:
			raise forms.ValidationError('That email address is registered by another user')

		return email
	
	def clean_password2(self):
		password1 = self.cleaned_data.get('password1')
		password2 = self.cleaned_data.get('password2')
		
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError('Your password and confirmation don\'t match')
		
		return password1
	
	def save(self, commit = True):
		changed_email = self.cleaned_data.get('change_email') != self.instance.email
		user = super(ProfileForm, self).save(commit = False)
		
		if self.cleaned_data.get('password1'):
			raise Exception('New password')
			user.set_password(self.cleaned_data['password1'])
		
		if commit:
			user.save()
		
		if changed_email:
			user.email_confirmations.create(
				network = self.network,
				email = self.cleaned_data.get('change_email')
			)
		
		if self.fields.get('avatar'):	
			try:
				profile = user.get_profile()
			except Profile.DoesNotExist:
				profile = Profile(user = user)
			
			profile.avatar = self.cleaned_data['avatar'][0]
			profile.save()
		
		return user
	
	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'username', 'change_email', 'avatar')

class ForgottenPasswordForm(forms.Form):
	username_or_email = forms.CharField(
		label = _('Username or email address')
	)
	
	def __init__(self, network, *args, **kwargs):
		super(ForgottenPasswordForm, self).__init__(*args, **kwargs)
		self.network = network
	
	def clean_username_or_email(self):
		field = self.cleaned_data['username_or_email']
		
		if not re.match(r'^[\w]+$', field) and not email_re.match(field):
			raise forms.ValidationError('That doesn\'t appear to be a username or an email address')
		
		return field
	
	def save(self, commit = True):
		from meegloo.registration.models import PasswordReset
		from django.db.models import Q
		
		field = self.cleaned_data['username_or_email']
		
		try:
			user = User.objects.get(
				Q(username__iexact = field) | Q(email__iexact = field)
			)
		except User.DoesNotExist:
			return None
		
		reset = PasswordReset(
			user = user,
			network = self.network
		)
		
		if commit:
			reset.save()
		
		return reset

class PasswordResetForm(forms.Form):
	password1 = forms.CharField(
		label = _('Set a new password'), min_length = 7, max_length = 20,
		widget = forms.PasswordInput,
		help_text = _('Choose something between 7 and 20 characters')
	)
	
	password2 = forms.CharField(
		label = _('Confirm your new password'), min_length = 7, max_length = 20,
		widget = forms.PasswordInput, help_text = _('Just to be on the safe side')
	)
	
	def clean_password2(self):
		password1 = self.cleaned_data.get('password1')
		password2 = self.cleaned_data.get('password2')
		
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError(u'Your password and confirmation don\'t match')
		
		return password1
	
	def __init__(self, reset, *args, **kwargs):
		super(PasswordResetForm, self).__init__(*args, **kwargs)
		self.reset = reset
	
	def save(self):
		password = self.cleaned_data['password1']
		
		self.reset.reset(password)