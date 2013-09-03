#!/usr/bin/env python
# encoding: utf-8

def html(request, handler):
	from django.http import HttpResponse, Http404, HttpResponseForbidden
	from meegloo.oembed.helpers import resolve
	import re
	
	referer = request.META.get('HTTP_REFERER')
	current = request.build_absolute_uri()
	
	if not referer:
		pass # return HttpResponseForbidden('URL cannot be accessed directly')
	else:
		referer_domain = re.match(r'^https?://([^/]+)/.*', referer)
		current_domain = re.match(r'^https?://([^/]+)/.*', current)
		
		if referer_domain and current_domain:
			referer_groups = referer_domain.groups()
			current_groups = current_domain.groups()
			
			if any(referer_groups) and any(current_groups):
				if referer_groups[0] != current_groups[0]:
					return HttpResponseForbidden('Cross-site requests are forbidden')
			else:
				return HttpResponseForbidden('Cannot determin referer URL')
		else:
			return HttpResponseForbidden('Cannot determin referer URL')
	
	url = request.GET.get('url')
	width = request.GET.get('width')
	
	try:
		width = int(width)
	except TypeError, ValueError:
		width = 0
	
	if not url:
		raise Http404('URL not specified')
	
	html = resolve(handler, url, width)
	return HttpResponse(html)