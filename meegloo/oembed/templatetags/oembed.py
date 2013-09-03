#!/usr/bin/env python
# encoding: utf-8

from django.template import Library
from django.utils.safestring import mark_safe
from meegloo.oembed.helpers import match, resolve

register = Library()
@register.inclusion_tag('oembed/json.inc.js', takes_context = True)
def oembed(context, url, div_id):
	handler = match(url)
	request = context.get('request')
	
	if handler:
		return {
			'url': url,
			'handler': handler,
			'div_id': div_id,
			'network': request.network
		}
	
	return {}

@register.simple_tag()
def oembed_nojson(url, width):
	handler = match(url)
	if handler:
		return mark_safe(
			resolve(handler, url, width)
		)
	
	return ''