#!/usr/bin/env python
# encoding: utf-8

from tempfile import mkstemp
from django.conf import settings
from django.core.files import File
from raven.contrib.django.handlers import SentryHandler
from meegloo.streams import POST_CONVERSION_FAILED, POST_CONVERTING, POST_UPLOADING, POST_LIVE
from threading import Thread
from functools import wraps
import os, subprocess, logging, mimetypes

class Converter(object):
	def __init__(self):
		self.logger = logging.getLogger('task')
		self.logger.setLevel(logging.DEBUG)
		self.logger.addHandler(SentryHandler())
		self.logger.debug('Conversion process ready')
	
	def create_temp_file(self, extension = '.tmp'):
		handle, filename = mkstemp(
			extension or '.tmp',
			dir = getattr(settings, 'TEMP_DIR')
		)
		
		os.close(handle)
		return filename
	
	def write_temp_file(self, source):
		handle, filename = mkstemp(
			dir = getattr(settings, 'TEMP_DIR')
		)
		
		self.logger.debug('Writing contents of file to temporary storage')
		
		try:
			os.write(handle, source)
		finally:
			os.close(handle)
		
		return filename
	
	def upload(self, obj, source_name):
		mimetypes.add_type('video/x-flv', 'flv', False)
		
		# Save the state of this media as uploading
		obj.post.state = POST_UPLOADING
		obj.post.save()
		obj.state = u'Uploading'
		obj.save()
		
		# Get the MIME type
		mime, encoding = mimetypes.guess_type(source_name)
		
		f = open(source_name)
		try:
			# Save the file in a format Django can upload to S3
			obj.post.media.create(
				mimetype = mime,
				content = File(
					f,
					name = '%s%s' % (
						os.path.splitext(source_name)[0],
						os.path.splitext(source_name)[-1]
					)
				)
			)
			
			return True
		finally:
			f.close()
	
	def commands(self, obj, command_list, source_name):
		dest_files = []
		
		try:
			for (extension, command) in command_list:
				dest_name = self.create_temp_file(extension)
				success, output = self.command(obj, command, source_name, dest_name)
				
				self.logger.debug('Converting %s' % source_name)
				
				d = {
					'command': command % (source_name, dest_name),
					'source': source_name,
					'dest': dest_name,
					'extension': extension,
					'output': output
				}
				
				if success:
					dest_files.append(dest_name)
					self.logger.info('Conversion successful',
						extra = {
							'data': d
						}
					)
				else:
					obj.post.delete()
					self.logger.error('Conversion failed',
						extra = {
							'data': d
						}
					)
					
					return False
			
			obj.post.state = POST_LIVE
			obj.post.save()
			
			if obj.post.tweet:
				obj.post.update_twitter()
			
			dest_files.append(source_name)
			return True
		finally:
			self.cleanup(obj, *dest_files)
	
	def command(self, obj, cmd, source_name, dest_name):
		output = subprocess.Popen(
			cmd % (source_name, dest_name),
			shell = True,
			stdout = subprocess.PIPE
		).stdout.read()
		
		obj.post.state = POST_CONVERTING
		obj.post.save()
		obj.state = u'Converting'
		obj.save()
		
		if os.stat(dest_name).st_size > 0:
			# Save the state of this media as uploading
			obj.post.state = POST_UPLOADING
			obj.post.save()
			obj.state = u'Uploading'
			obj.save()
			
			# Get the MIME type
			mime, encoding = mimetypes.guess_type(dest_name)
			if os.path.splitext(dest_name)[-1] == '.flv':
				mime = 'video/x-flv'
			
			if not mime:
				raise Exception('Cannot guess MIME type for %s' % dest_name)
			
			# Save the file in a format Django can upload to S3
			obj.post.media.create(
				mimetype = mime,
				content = File(
					open(dest_name),
					name = '%s%s' % (
						os.path.splitext(dest_name)[0],
						os.path.splitext(dest_name)[-1]
					)
				)
			)
			
			return True, output
		else:
			return False, output
	
	def cleanup(self, obj, *files):
		for f in files:
			os.remove(f)
		
		obj.delete()

def run_async(func):
	@wraps(func)
	def async_func(*args, **kwargs):
		func_hl = Thread(target = func, args = args, kwargs = kwargs)
		func_hl.start()
		return func_hl

	return async_func