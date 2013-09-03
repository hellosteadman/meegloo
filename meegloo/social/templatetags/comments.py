#!/usr/bin/env python
# encoding: utf-8

from django.template import Library
from django.contrib.contenttypes.models import ContentType
from meegloo.social.models import Comment
from meegloo.social.forms import CommentForm
register = Library()

@register.inclusion_tag('social/form.inc.html', takes_context = True)
def comment_form(context, obj):
	request = context.get('request')
	ct = ContentType.objects.get_for_model(obj)
	
	if not request or request.user.is_anonymous():
		return {
			'content_type': ct,
			'obj': obj
		}
	
	form = CommentForm(
		instance = Comment(
			content_type = ct,
			object_id = obj.pk,
			author = request.user,
			network = request.network
		)
	)
	
	return {
		'form': form,
		'content_type': ct,
		'obj': obj
	}