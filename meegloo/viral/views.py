#!/usr/bin/env python
# encoding: utf-8

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.http import Http404, HttpResponseRedirect
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.utils.translation import ugettext as _
from meegloo.registration.forms import RegistrationForm
from meegloo.viral.models import Competition, Entrant
from datetime import datetime

def register(request, guid = None):
	if guid:
		entrant = get_object_or_404(Entrant, guid = guid)
		competition = entrant.competition
	else:
		entrant = None
		try:
			competition = Competition.objects.active().latest()
		except Competition.DoesNotExist:
			raise Http404('No competitions on at the moment')
	
	if not competition.is_active() or (entrant and not entrant.is_valid()):
		raise Http404('Competition link not valid')
	
	if request.user.is_authenticated():
		messages.add_message(
			request,
			messages.ERROR,
			_('Sorry, you can only enter once')
		)
		
		return HttpResponseRedirect(
			reverse('competition_leaderboard')
		)
	
	form = RegistrationForm(
		data = request.POST or None,
		prefix = 'signup'
	)
	
	if request.method == 'POST' and form.is_valid():
		user = form.save()
		user.email_confirmations.create(
			network = request.network
		)
		
		entrant = Entrant.objects.create(
			competition = competition,
			user = user,
			parent = entrant
		)
		
		if entrant.parent:
			entrant.parent.actions.create(
				text = u'Recruited %s' % user.username,
				points = 100,
				content_type = ContentType.objects.get_for_model(user),
				object_id = user.pk
			)
		
		messages.add_message(
			request,
			messages.SUCCESS,
			_('Thanks for signing up. Welcome aboard!')
		)
		
		return TemplateResponse(
			request,
			'viral/confirm.html',
			{
				'competition': competition,
				'entry': entrant,
				'title_parts': (competition.headline,)
			}
		)
	
	return TemplateResponse(
		request,
		'viral/signup.html',
		{
			'competition': competition,
			'form': form,
			'title_parts': (competition.headline,)
		}
	)
	
def leaderboard(request):
	try:
		competition = Competition.objects.active().latest()
	except Competition.DoesNotExist:
		raise Http404('No competitions on at the moment')
	
	if request.user.is_authenticated():
		try:
			entry = Entrant.objects.get(
				competition = competition,
				user = request.user,
				barred = False
			)
		except Entrant.DoesNotExist:
			entry = None
	else:
		entry = None
	
	return TemplateResponse(
		request,
		'viral/leaderboard.html',
		{
			'competition': competition,
			'leaderboard': competition.entrants.leaderboard(),
			'title_parts': (u'Leaderboard', competition.headline),
			'entry': entry
		}
	)