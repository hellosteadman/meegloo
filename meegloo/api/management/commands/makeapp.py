#!/usr/bin/env python
# encoding: utf-8

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
	def handle(self, *args, **options):
		from django.contrib.auth.models import User
		from piston.models import Consumer
		
		app = Consumer(status = 'accepted')
		username = raw_input('Username of the app\'s owner: ')
		
		while not username:
			username = raw_input('Username of the app\'s owner (required): ')
		
		try:
			app.user = User.objects.get(username = username)
		except User.DoesNotExist:
			raise CommandError('User %s not found' % username)
		
		name = raw_input('App name: ')
		while not name:
			name = raw_input('App name (required): ')
		
		app.name = name
		app.description = raw_input('App description (optional): ')
		app.generate_random_codes()
		
		app.save()
		print '\nApplication name: %s\nApplication creator: %s\nAPI key: %s\nAPI secret: %s' % (
			app.name,
			app.user.get_full_name() or app.user.username,
			app.key,
			app.secret
		)