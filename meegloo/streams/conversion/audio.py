#!/usr/bin/env python
# encoding: utf-8

from meegloo.streams.conversion import run_async
import logging

@run_async
def convert(source, pk):
	from meegloo.streams.models import Conversion
	from meegloo.streams.conversion import Converter
	from django.conf import settings
	
	logger = logging.getLogger('task')
	
	try:
		converter = Converter()
		conversion = Conversion.objects.get(pk = pk)
		
		converter.commands(conversion,
			settings.ENCODING_COMMANDS.get('AUDIO'),
			source
		)
	except Exception, ex:
		logger.error(unicode(ex))