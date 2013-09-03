#!/usr/bin/env python
# encoding: utf-8

class ContentTypeMiddleware(object):
	def process_request(self, request):
		if request.path.startswith('/api/'):
			if 'CONTENT_TYPE' in request.META:
				request.META['CONTENT_TYPE'] = request.META['CONTENT_TYPE'].replace(
					'; charset=utf-8', ''
				)
		
		return None
		
	def process_exception(self, request, exception):
		from django.http.multipartparser import MultiPartParserError
		from django.http import HttpResponse
		
		if isinstance(exception, (MultiPartParserError, IOError)):
			return HttpResponse('', mimetype = 'text/plain')