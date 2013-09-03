#!/usr/bin/env python
# encoding: utf-8

from meegloo.viral.models import Competition, Entrant

def competitions(request):
	d = {}
	
	try:
		competitions = Competition.objects.active()
		
		if request.user.is_authenticated():
			competitions = competitions.exclude(
				entrants__user = request.user
			)
			
			try:
				d['competition_entry'] = Entrant.objects.active().get(user = request.user)
			except Entrant.DoesNotExist:
				pass
		
		d['active_competition'] = competitions.get(network = request.network)
	except Competition.DoesNotExist:
		pass
	
	return d