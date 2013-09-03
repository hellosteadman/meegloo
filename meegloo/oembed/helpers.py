#!/usr/bin/env python
# encoding: utf-8

def match(url):
	from meegloo.oembed import URL_PATTERNS
	import re
	
	for handler, (pattern, endpoint, format) in URL_PATTERNS.items():
		if not re.match(pattern, url, re.IGNORECASE) is None:
			return handler

def resolve(handler, url, width):
	from django.core.cache import cache
	from meegloo.oembed import URL_PATTERNS
	from urllib import urlencode
	from urllib2 import Request, urlopen, HTTPError
	import re
	
	try:
		pattern, endpoint, format = URL_PATTERNS[handler]
	except KeyError:
		raise Http404('Handler not found')
	
	if format == 'json':
		mimetype = 'application/json'
	elif format == 'xml':
		mimetype = 'text/xml'
	elif format != 'html':
		raise Exception('Handler configured incorrectly (unrecognised format %s)' % format)
	
	params = {
		'url': url
	}
	
	if width > 0:
		params['width'] = width
		params['maxwidth'] = width
	
	if not callable(endpoint):
		endpoint = endpoint % urlencode(params)
		cache_key = 'oemved__%s__%s' % (
			handler,
			re.sub(r'\W+', '', endpoint.encode('base64')),
		)
	else:
		cache_key = 'oemved__%s__%s__%s' % (
			handler,
			re.sub(r'\W+', '', str(endpoint).encode('base64')),
			re.sub(r'\W+', '', url.encode('base64')),
		)
	
	try:
		html = cache.get(cache_key)
	except:
		html = None
	
	if not html:
		if not callable(endpoint):
			oembed_request = Request(
				endpoint, headers = {
					'Accept': mimetype,
					'User-Agent': 'Meegloo/oembed'
				}
			)
			
			try:
				response = urlopen(oembed_request)
			except HTTPError, ex:
				raise Http404(ex.msg)
			
			if format == 'json':
				from django.utils import simplejson
			
				try:
					json = simplejson.load(response)
				except:
					raise Http404('Not a JSON response')
				
				if 'html' in json:
					html = json.get('html')
				elif 'thumbnail_url' in json:
					html = '<a href="%(resource)s"><img alt=="%(title)s" src="%(url)s" /></a>' % {
						'title': json['title'],
						'url': json['thumbnail_url'],
						'resource': url,
					}
			else:
				from elementtree import ElementTree
				
				try:
					xml = ElementTree.parse(response)
				except:
					raise Http404('Not an XML response')
				
				try:
					html = xml.getroot().find('html').text or ''
				except:
					if not xml.find('url') is None:
						html = '<a href="%(resource)s"><img alt=="%(title)s" src="%(url)s" /></a>' % {
							'title': xml.find('title') and xml.find('title').text or '',
							'url': xml.find('url').text,
							'resource': url
						}
					else:
						raise Http404('No embeddable content')
		else:
			html = endpoint(url) or '<p><a href="%(url)s" target="_blank">%(url)s</a></p>' % {
				'url': url
			}
		
		try:
			cache.set(cache_key, html, 60 * 60)
		except:
			pass
			
	return html