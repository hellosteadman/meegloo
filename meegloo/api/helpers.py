#!/usr/bin/env python
# encoding: utf-8

def format_errors(value):
	from django.core.exceptions import ValidationError
	
	if isinstance(value, ValidationError):
		if hasattr(value, 'message_dict'):
			value = value.message_dict
		else:
			value = str(value)
	
	return '\n\n'.join(
		[
			k == '__all__' and ''.join(v) or '%s: %s' % (k, ''.join(v))
			for (k, v) in value.items()
		]
	)