#!/usr/bin/env python
# encoding: utf-8

def upload_logo(instance, filename):
	from os import path
	
	return '/'.join(
		(
			'networks',
			instance.domain,
			'logo%s' % path.splitext(filename)[-1]
		)
	)

def upload_icon(instance, filename):
	from os import path
	
	return '/'.join(
		(
			'networks',
			instance.domain,
			'icon%s' % path.splitext(filename)[-1]
		)
	)