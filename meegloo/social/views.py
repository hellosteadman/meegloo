#!/usr/bin/env python
# encoding: utf-8

from django.template.response import TemplateResponse
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from meegloo.social.models import Comment, Question, Poll, PollOption, PollAnswer
from meegloo.social.forms import CommentForm

@require_POST
@login_required
def post_comment(request, app_label, model, object_id):
	ct = get_object_or_404(ContentType, app_label = app_label, model = model)
	obj = get_object_or_404(ct.model_class(), pk = object_id)
	
	form = CommentForm(request.POST,
		instance = Comment(
			content_type = ct,
			object_id = obj.pk,
			author = request.user,
			network = request.network
		)
	)
	
	if form.is_valid():
		comment = form.save()
		
		messages.add_message(
			request,
			messages.SUCCESS,
			u'Your comment has been posted'
		)
	else:
		messages.add_message(
			request,
			messages.ERROR,
			form.errors
		)
	
	return HttpResponseRedirect(
		'%s#post' % obj.get_absolute_url()
	)

@require_POST
@login_required
def answer_question(request, app_label, model, object_id):
	ct = get_object_or_404(ContentType, app_label = app_label, model = model)
	obj = get_object_or_404(ct.model_class(), pk = object_id)
	answer = request.POST.get('answer')
	
	if not answer:
		return HttpResponse('')
	
	try:
		question = Poll.objects.get(
			content_type = ct,
			object_id = obj.pk
		)
		
		try:
			answer = int(answer)
		except TypeError, ValueError:
			return HttpResponse('')
		
		option = question.options.get(
			pk = answer
		)
		
		PollAnswer.objects.filter(
			question = question,
			user = request.user
		).delete()
		
		PollAnswer.objects.create(
			question = question,
			option = option,
			text = option.label,
			user = request.user
		)
	
	except Poll.DoesNotExist:
		question = Question.objects.get(
			content_type = ct,
			object_id = obj.pk
		)
		
		question.answers.create(
			user = request.user,
			text = answer
		)
	except Question.DoesNotExist:
		raise Http404()
	
	if request.is_ajax():
		return TemplateResponse(
			request,
			'social/answers.inc.html',
			{
				'question': question
			}
		)
	else:
		return HttpResponseRedirect(obj.get_absolute_url())