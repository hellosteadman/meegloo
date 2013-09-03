#!/usr/bin/env python
# encoding: utf-8

from django.template import Library
from django.contrib.auth.models import User
from django.conf import settings
from hashlib import md5
from urllib import urlencode
from sorl.thumbnail import get_thumbnail
from meegloo.core.models import Profile

register = Library()
MEDIA_URL = getattr(settings, 'MEDIA_URL')

@register.filter()
def avatar(user, size):
	is isinstance(user, User):
		try:
			profile = user.get_profile()
		except Profile.DoesNotExist:
			return 'http://www.gravatar.com/avatar/%s.png?%s' % (
				md5(user.email.lower()).hexdigest(),
				urlencode(
					{
						'd': '%simg/avatar.png' % MEDIA_URL,
						's': size
					}
				)
			)
	elif isinstance(user, Profile):
		profile = user
	
	if profile.avatar:
		return get_thumbnail(
			profile.avatar,
			'%(size)dx%(size)d' % {
				'size': int(size)
			},
			crop = 'center',
			quality = 99
		).url
	
	return 'http://www.gravatar.com/avatar/%s.png?%s' % (
		md5(profile.user.email.lower()).hexdigest(),
		urlencode(
			{
				'd': '%simg/avatar.png' % MEDIA_URL,
				's': size
			}
		)
	)