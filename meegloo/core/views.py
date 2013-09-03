#!/usr/bin/env python
# encoding: utf-8

from django.conf import settings
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.template.response import TemplateResponse
from haystack.forms import ModelSearchForm, FacetedSearchForm
from haystack.query import EmptySearchQuerySet

RESULTS_PER_PAGE = getattr(settings, 'HAYSTACK_SEARCH_RESULTS_PER_PAGE', 20)

def search(request):
	query = ''
	results = EmptySearchQuerySet()
	
	if request.GET.get('q'):
		form = ModelSearchForm(request.GET)
		
		if form.is_valid():
			query = form.cleaned_data['q']
			results = form.search().filter(network = request.network.parent)
	else:
		form = ModelSearchForm()
	
	paginator = Paginator(results, RESULTS_PER_PAGE)
	
	try:
		page = paginator.page(
			int(request.GET.get('page', 1))
		)
	except InvalidPage:
		raise Http404('No such page')
	
	context = {
		'form': form,
		'page': page,
		'paginator': paginator,
		'query': query,
		'suggestion': None,
	}
	
	if getattr(settings, 'HAYSTACK_INCLUDE_SPELLING', False):
		context['suggestion'] = form.get_suggestion()
	
	return TemplateResponse(
		request,
		'core/search.html',
		context
	)