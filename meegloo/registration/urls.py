#!/usr/bin/env python
# encoding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('',
	url(r'^login/$', 'django.contrib.auth.views.login', name = 'login'),
	url(r'^logout/$', 'django.contrib.auth.views.logout', name = 'logout'),
	url(r'^profile/$', 'meegloo.registration.views.profile', name = 'profile'),
	url(r'^profile/edit/$', 'meegloo.registration.views.edit_profile', name = 'edit_profile'),
	url(r'^signup/$', 'meegloo.registration.views.register', name = 'register'),
	url(r'^signup/confirm/$', 'django.views.generic.simple.direct_to_template',
		{
			'template': 'registration/confirm.html'
		}, name = 'register_confirmation'
	),
	url(r'^confirm-email/$', 'meegloo.registration.views.confirm_email', name = 'confirm_email'),
	url(r'^forgot-password/$', 'meegloo.registration.views.forgot_password', name = 'forgot_password'),
	url(r'^reset-password/$', 'meegloo.registration.views.reset_password', name = 'reset_password'),
	url(r'^oauth/', include('meegloo.registration.oauth.urls')),
)