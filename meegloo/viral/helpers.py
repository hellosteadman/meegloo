#!/usr/bin/env python
# encoding: utf-8

from django.contrib.contenttypes.models import ContentType

def stream_post_save(sender, instance, created, **kwargs):
	if created and instance.part_of.contributors.count() == 1:
		for entrant in instance.profile.competition_entries.eligible().active().filter(
			competition__network = instance.part_of.network
		):
			entrant.actions.create(
				text = u'Created a new stream',
				points = 25,
				content_type = ContentType.objects.get_for_model(instance),
				object_id = instance.pk
			)

def post_post_save(sender, instance, created, **kwargs):
	if created:
		for entrant in instance.author.competition_entries.eligible().active().filter(
			competition__network = instance.stream.part_of.network
		):
			entrant.actions.create(
				text = u'Created a new post',
				points = {
					'text': 1,
					'url': 2,
					'question': 4,
					'poll': 5,
					'slide': 10,
					'photo': 25,
					'audio': 50,
					'video': 100
				}[instance.kind],
				content_type = ContentType.objects.get_for_model(instance),
				object_id = instance.pk
			)

def comment_post_save(sender, instance, created, **kwargs):
	if created:
		for entrant in instance.author.competition_entries.eligible().active().filter(
			competition__network = instance.network
		):
			entrant.actions.create(
				text = u'Posted a comment',
				points = 3,
				content_type = ContentType.objects.get_for_model(instance),
				object_id = instance.pk
			)

def answer_post_save(sender, instance, created, **kwargs):
	if created:
		for entrant in instance.author.competition_entries.eligible().active().filter(
			competition__network = instance.network
		):
			entrant.actions.create(
				text = u'Answered a question',
				points = 3,
				content_type = ContentType.objects.get_for_model(instance),
				object_id = instance.pk
			)