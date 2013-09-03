#!/usr/bin/env python
# encoding: utf-8

from django.template import Library
from django.contrib.contenttypes.models import ContentType
from meegloo.social.models import Question, Poll, PollAnswer

register = Library()

@register.inclusion_tag('social/question.inc.html', takes_context = True)
def question_form(context, obj):
	question = Question.objects.get(
		content_type = ContentType.objects.get_for_model(obj),
		object_id = obj.pk
	)
	
	return {
		'question': question,
		'is_authenticated': context['request'].user.is_authenticated(),
		'api': context.get('api')
	}

@register.inclusion_tag('social/poll.inc.html', takes_context = True)
def poll_form(context, obj):
	question = Poll.objects.get(
		content_type = ContentType.objects.get_for_model(obj),
		object_id = obj.pk
	)
	
	user = context['request'].user
	
	return {
		'question': question,
		'is_authenticated': user.is_authenticated(),
		'has_voted': user.is_authenticated() and (
			PollAnswer.objects.filter(question = question, user = user).count() > 0
		) or False,
		'api': context.get('api')
	}
	
@register.inclusion_tag('social/answers.inc.html')
def question_answers(obj):
	question = Question.objects.get(
		content_type = ContentType.objects.get_for_model(obj),
		object_id = obj.pk
	)
	
	return {
		'question': question
	}
	
@register.filter
def percentof(val, total):
	return float(val) / float(total) * 100.0