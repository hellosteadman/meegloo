#!/usr/bin/env python
# encoding: utf-8

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from optparse import make_option

class Command(BaseCommand):
	@transaction.commit_manually
	def handle(self, *args, **options):
		from meegloo.streams.models import Trend
		
		try:
			Trend.objects.rebuild()
			transaction.commit()
		except:
			transaction.rollback()
			raise