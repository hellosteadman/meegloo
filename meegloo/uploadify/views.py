#!/usr/bin/env python
# encoding: utf-8

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from meegloo.uploadify.models import Upload

@csrf_exempt
def upload(request, *args, **kwargs):
	from mimetypes import guess_type
	from django.conf import settings
	from os import path
	import logging
	
	logger = logging.getLogger()
	
	try:
		if request.method == 'POST' and request.FILES:
			if not 'guid' in request.POST or not 'user' in request.POST:
				return HttpResponse('')
			
			data = request.FILES['Filedata']
			filename = path.join(
				getattr(settings, 'TEMP_DIR'),
				request.POST['guid'] + path.splitext(data.name)[-1]
			)
			
			f = open(filename, 'w')
			try:
				f.write(data.read())
			finally:
				f.close()
			
			Upload.objects.create(
				guid = request.POST['guid'],
				filename = filename
			)
			
			return HttpResponse('True')
	
		return HttpResponse('')
	except Exception, ex:
		logger.error(ex)