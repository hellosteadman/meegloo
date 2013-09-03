#!/usr/bin/env python
# encoding: utf-8

def forms(request):
	from meegloo.registration.forms import RegistrationForm
	from django.contrib.auth.forms import AuthenticationForm
	
	return {
		'login_form': AuthenticationForm(),
		'signup_form': request.method == 'GET' and RegistrationForm(prefix = 'signup') or None
	}