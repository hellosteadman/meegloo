#!/usr/bin/env python
# encoding: utf-8

from django.http import HttpResponseBadRequest
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from piston.handler import BaseHandler
from meegloo.streams.models import Stream, UserStream, Trend, Category
from meegloo.api.helpers import format_errors

def search_streams(streams, criteria, parent = 'part_of'):
	words = criteria.split(' ')
	
	q = Q()
	for word in words:
		if word:
			q |= Q(
				**{
					'%s__name__icontains' % parent: word
				}
			) | Q(
				**{
					'%s__category__name__icontains' % parent: word
				}
			)
	
	if len(words) == 1:
		q = Q(q) | Q(
			**{
				'%s__slug__iexact' % parent: word
			}
		) | Q(
			**{
				'%s__tags__tag__iexact' % parent: word
			}
		)
	
	return streams.filter(q)

class StreamHandler(BaseHandler):
	model = UserStream
	exclude = ('_state',)
	
	"""
	This interface allows for listing and creation of Meegloo streams.
	"""
	
	def read(self, request, slug = None):
		"""
		Returns a list of streams, or a specific stream identified by ''slug''.
		"""
		
		if slug:
			result = get_object_or_404(Stream, network = request.network, slug = slug)
			return {
				'id': result.pk,
				'name': result.name,
				'slug': result.slug,
				'contributors': [
					r.profile for r in result.contributors.public().only('profile')
				],
				'category': result.category
			}
		else:
			result = super(StreamHandler, self).read(request).filter(
				part_of__network = request.network
			).public()
			
			if request.GET.get('q'):
				result = search_streams(result, request.GET['q'])
			
			values = result.values_list(
				'part_of__id', 'part_of__name', 'part_of__slug', 'part_of__category__name'
			).distinct().order_by(
				'-part_of__updated'
			)
		
		l = []
		for triple in values:
			pk, name, slug, category = triple
			
			l.append(
				{
					'id': pk,
					'name': name,
					'slug': slug,
					'category': category
				}
			)
		
		return l
	
	def create(self, request):
		name = request.POST.get('name')
		slug = request.POST.get('slug')
		twitter = request.POST.get('twitter')
		flickr = request.POST.get('flickr')
		category = request.POST.get('category')
		
		if not slug:
			from django.template.defaultfilters import slugify
			slug = slugify(name)
		
		if category:
			try:
				category = Category.objects.get(pk = category)
			except Exception, ex:
				return HttpResponseBadRequest(unicode(ex))
		else:
			category = Category.objects.get(pk = 5)
		
		if Stream.objects.filter(network = request.network, slug__iexact = slug).count() == 0:
			if request.GET.get('join'):
				return HttpResponseBadRequest('New streams cannot be created with join option')
			
			if not name:
				return HttpResponseBadRequest('name is required')
			
			stream = Stream(
				name = name,
				slug = slug,
				network = request.network,
				category = category
			)
			
			try:
				stream.full_clean()
				stream.save()
			except ValidationError, ex:
				return HttpResponseBadRequest(
					format_errors(ex)
				)
		else:
			stream = Stream.objects.get(
				slug__iexact = slug,
				network = request.network
			)
		
		if UserStream.objects.filter(
			part_of = stream,
			profile = request.user
		).count() == 0:
			user_stream = UserStream(
				part_of = stream,
				profile = request.user
			)
			
			try:
				user_stream.full_clean()
				user_stream.save()
				
				if twitter:
					if twitter.startswith('#'):
						twitter = twitter[1:]
					
					stream.tags.get_or_create(
						user = request.user,
						domain = 'twitter.com',
						tag = twitter.lower().strip()
					)
				
				if flickr:
					stream.tags.get_or_create(
						user = request.user,
						domain = 'flickr.com',
						tag = flickr.lower().strip()
					)
				
				return user_stream
			except ValidationError, ex:
				return HttpResponseBadRequest(
					format_errors(ex)
				)
		elif not request.POST.get('join'):
			return HttpResponseBadRequest(
				'Stream %s already exists' % slug
			)
		else:
			return UserStream.objects.get(part_of = stream, profile = request.user)
	
	def delete(self, request, slug):
		self.queryset(request).get(
			part_of__slug = stream,
			part_of__network = request.network,
			profile = request.author,
			slug = slug
		).delete()
		
		return rc.DELETED

class MyStreamHandler(BaseHandler):
	allowed_methods = ('GET',)
	
	def read(self, request):
		values = UserStream.objects.filter(
			profile = request.user,
			part_of__network = request.network
		)
		
		if request.GET.get('q'):
			values = search_streams(values, request.GET['q'])
		
		values = values.values_list('part_of__pk', 'part_of__name', 'part_of__slug', 'part_of__category__name')
		values = values[:10]
		
		l = []
		for (pk, name, slug, category) in values:
			l.append(
				{
					'id': pk,
					'name': name,
					'slug': slug,
					'category': category
				}
			)
		
		return l

class FollowingStreamHandler(BaseHandler):
	allowed_methods = ('GET',)
	
	def read(self, request):
		values = UserStream.objects.filter(
			profile__in = request.user.following.values_list('followee', flat = True),
			part_of__network = request.network
		)
		
		if request.GET.get('q'):
			values = search_streams(values, request.GET['q'])
		
		values = values.values_list(
			'part_of__pk', 'part_of__name', 'part_of__slug',
			'part_of__category__name'
		)
		
		values = values[:10]
		
		l = []
		for (pk, name, slug, category) in values:
			l.append(
				{
					'id': pk,
					'name': name,
					'slug': slug,
					'category': category,
					'profiles': User.objects.filter(
						streams__part_of__pk = pk,
						pk__in = request.user.following.values_list('followee__pk', flat = True)
					).values_list('username', flat = True)
				}
			)
		
		return l

class NearbyStreamHandler(BaseHandler):
	"""
	Returns the 10 nearest streams to a location specified by ``lst`` and ``long`` arguments.
	"""
	
	allowed_methods = ('GET',)
	
	def read(self, request):
		if not request.GET.get('lat') or not request.GET.get('long'):
			return HttpResponseBadRequest('lat and long are required')
		
		try:
			values = UserStream.objects.filter(
				part_of__network = request.network
			).public().near(
				float(request.GET.get('lat')),
				float(request.GET.get('long'))
			).live().distinct()
			
			if request.GET.get('q'):
				values = search_streams(values, request.GET['q'])
			
			values = values[:10]
		except ValueError:
			return HttpResponseBadRequest('lat and/or long values invalid')
		
		values = values.values_list('part_of__pk', 'part_of__name', 'part_of__slug', 'part_of__category__name')
		
		l = []
		for (pk, name, slug, category) in values:
			l.append(
				{
					'id': pk,
					'name': name,
					'slug': slug,
					'category': category
				}
			)

		return l
	
class TrendingStreamHandler(BaseHandler):
	"""
	Returns the 10 most popular streams
	"""
	
	allowed_methods = ('GET',)
	model = Trend
	
	def read(self, request):
		values = super(TrendingStreamHandler, self).read(request).filter(
			stream__network = request.network
		).values_list(
			'stream__id', 'stream__name', 'stream__slug', 'stream__category__name'
		)
		
		if request.GET.get('q'):
			values = search_streams(values, request.GET['q'], 'stream')
		
		values = values.distinct()[:10]
		
		l = []
		for (pk, name, slug, category) in values:
			l.append(
				{
					'id': pk,
					'name': name,
					'slug': slug,
					'category': category
				}
			)

		return l

class CategoryHandler(BaseHandler):
	allowed_methods = ('GET',)
	model = Category
	fields = ('id', 'name', 'slug')