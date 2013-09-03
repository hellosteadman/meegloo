#!/usr/bin/env python
# encoding: utf-8

from django.template import Library

register = Library()
@register.filter
def gravatar(email, size = 60):
	from django.utils.safestring import mark_safe
	from hashlib import md5
	
	return mark_safe(
		'http://www.gravatar.com/avatar/%s.jpg?d=identicon&s=%d' % (
			md5(email.lower()).hexdigest(), int(size)
		)
	)