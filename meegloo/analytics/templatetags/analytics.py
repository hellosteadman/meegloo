#!/usr/bin/env python
# encoding: utf-8

from django.template import Library

register = Library()

@register.inclusion_tag('analytics/google.inc.html', takes_context = True)
def google_analytics(context):
	from django.conf import settings
	
	request = context.get('request')
	if not request is None:
		if request.user.is_authenticated() and request.user.is_staff:
			return {}
		
		return {
			'ids': getattr(settings, 'GOOGLE_ANALYTICS_IDS', ())
		}
	
	return {'ids': []}