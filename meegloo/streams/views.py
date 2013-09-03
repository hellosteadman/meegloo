#!/usr/bin/env python
# encoding: utf-8

from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.cache import never_cache
from django.utils import simplejson
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, timedelta
from meegloo.core.models import Profile
from meegloo.streams import POST_CONVERTING, POST_LIVE
from meegloo.streams.models import Stream, UserStream, StreamEmbed, Post, Set, Category
from meegloo.streams.forms import PostForm, UserStreamForm, StreamEmbedForm
from meegloo.streams.helpers import clean_domain
import re, logging

def streams(request):
	return TemplateResponse(
		request,
		'streams/list.html',
		{
			'streams': Stream.objects.filter(
				network = request.network
			).public().order_by(
				'-updated'
			)[:20],
			'body_classes': ('streams',),
			'title_parts': (u'Join a stream',)
		}
	)

@login_required
def my_streams(request):
	from django.utils import simplejson
	
	streams = [
		{
			'slug': stream.part_of.slug,
			'name': stream.part_of.name,
			'url': 'http://%s.%s%s' % (
				request.user.username,
				request.network.domain,
				stream.get_absolute_url()
			)
		} for stream in request.user.streams.filter(
			part_of__network = request.network
		).order_by('-updated')[:5]
	]
	
	return HttpResponse(
		simplejson.dumps(streams),
		mimetype = 'application/json'
	)

def can_embed(request, stream):
	extra = {
		'data': {
			'stream': stream.name
		}
	}
	
	logger = logging.getLogger()
	
	if 'key' in request.GET and 'domain' in request.GET:
		try:
			embedder = Profile.objects.get(embed_key_hashed = request.GET['key'])
		except Profile.DoesNotExist:
			logger.warn('Embed attempt with invalid key', extra = extra)
			return False
		
		try:
			user_stream = stream.contributors.get(profile = embedder.user)
		except UserStream.DoesNotExist:
			logger.warn(
				'Attempt by %s to embed a stream they don\'t own', embedder.user.username,
				extra = extra
			)
			
			return False
		
		domain = request.GET.get('domain')
		StreamEmbed.objects.get_or_create(
			stream = user_stream,
			domain = domain
		)
	else:
		referer = request.META.get('HTTP_REFERER')
		
		try:
			domain = re.match(r'^https?://([^/]+)/.*', referer).groups()[0]
		except:
			logger.warn('Attempt to access embed script directly', extra = extra)
			return False
		
		if StreamEmbed.objects.filter(
			stream__part_of = stream,
			domain__iexact = domain
		).count() == 0:
			logger.warn(
				'Attempt to access embed script from unauthorised domain: %s', domain,
				extra = extra
			)
			
			return False
	
	return True

@never_cache
def posts(request, **kwargs):
	stream = kwargs.get('stream')
	category = kwargs.get('category')
	kind = kwargs.get('kind')
	format = kwargs.get('format', 'standard')
	
	extension, mimetype, page_size = {
		'embed': ('js', 'text/javascript', 10),
		'iframe': ('iframe.html', 'text/html', 10),
		'standard': ('html', 'text/html', 10),
		'rss': ('rss', 'application/rss+xml', 100),
		'atom': ('atom', 'application/atom+xml', 100)
	}[format]
	
	if request.method == 'POST' and request.user.is_authenticated():
		from uuid import uuid4
		
		post_form = PostForm(request.POST, request.FILES)
		if post_form.is_valid():
			post = post_form.save(commit = False)
			post.author = request.user
			post.stream = UserStream.objects.get(
				part_of__pk = request.POST.get('stream'),
				part_of__network = request.network,
				profile = request.user
			)
			
			post.save()
			
			if post.conversions.count() == 0 and post.tweet:
				post.update_twitter()
			
			if request.is_ajax():
				return HttpResponse(
					simplejson.dumps(
						{
							'resp': True,
							'guid': str(uuid4())
						}
					),
					mimetype = 'text/javascript'
				)
		elif request.is_ajax():
			return HttpResponse(
				simplejson.dumps(
					{
						'errors': post_form.errors,
						'guid': str(uuid4())
					}
				),
				mimetype = 'text/javascript'
			)
	
	templates = [
		'%s/streams/posts.%s' % (request.network.domain, extension),
		'streams/posts.%s' % extension
	]
	
	body_classes = []
	title_parts = []
	can_post = False
	user_streams = None
	related_streams = None
	coords = None
	
	if request.profile:
		other_streams = request.profile.streams.filter(
			part_of__network = request.network
		).public()
		
		templates.insert(0, 'streams/profile/posts.%s' % extension)
		templates.insert(0, '%s/streams/profile/posts.%s' % (request.network.domain, extension))
		
		body_classes.append('user-stream')
	else:
		other_streams = None
		body_classes.append('public-stream')
	
	if stream:
		if request.profile:
			stream = get_object_or_404(UserStream,
				part_of__slug = stream,
				part_of__network = request.network,
				profile = request.profile
			)
			
			category = stream.part_of.category
			
# 			if stream.part_of.latitude and stream.part_of.longitude:
# 				coords = (stream.part_of.latitude, stream.part_of.longitude)
			
			posts = stream.posts.all()
			stream_tags = stream.part_of.tags.all()
			
			body_classes.append('specific-stream')
			if request.user.is_authenticated():
				can_post = request.user.pk == request.profile.pk
			
			title_parts.insert(0, request.profile.get_full_name() or request.profile.username)
			title_parts.insert(0, stream.part_of.name)
			
			if format in ('embed', 'iframe') and not 'callback' in request.GET:
				if not can_embed(request, stream.part_of):
					if(format == 'embed'):
						return HttpResponse(
							'alert("Meegloo stream embedding is not enabled on this domain.")',
							mimetype = 'text/javascript'
						)
					else:
						return HttpResponse(
							'Meegloo stream embedding is not enabled on this domain.'
						)
			
			reporters = User.objects.filter(
				pk__in = stream.part_of.contributors.public().values_list('profile__pk')
			)
		else:
			stream = get_object_or_404(Stream,
				slug = stream,
				network = request.network
			)
			
# 			if stream.latitude and stream.longitude:
# 				coords = (stream.latitude, stream.longitude)
			
			category = stream.category
			posts = Post.objects.filter(stream__part_of = stream, stream__private = False)
			stream_tags = stream.tags.all()
			
			if request.user.is_authenticated():
				can_post = stream.contributors.filter(profile = request.user).count() > 0
			
			title_parts.insert(0, stream)
			
			if format in ('embed', 'iframe') and not 'callback' in request.GET:
				if not can_embed(request, stream):
					if(format == 'embed'):
						return HttpResponse(
							'alert("Meegloo stream embedding is not enabled on this domain.")',
							mimetype = 'text/javascript'
						)
					else:
						return HttpResponse(
							'Meegloo stream embedding is not enabled on this domain.'
						)
			
			reporters = User.objects.filter(
				pk__in = stream.contributors.public().values_list('profile__pk')
			)
		
		if other_streams:
			other_streams = other_streams.exclude(pk = stream.pk).public()
	else:
		if request.profile:
			posts = Post.objects.filter(
				stream__profile = request.profile,
				stream__private = False,
				stream__part_of__network = request.network
			)
			
			templates.insert(0, 'posts.%s' % extension)
			templates.insert(0, '%s/posts.%s' % (request.network.domain, extension))
			body_classes.append('all-streams')
		else:
			posts = Post.objects.filter(
				kind__in = ('photo', 'video'),
				stream__private = False,
				stream__part_of__network = request.network
			)
			
			if category:
				categories = category.split('/')
				category = None
				
				for cat in categories:
					category = get_object_or_404(Category, slug = cat, parent = category)
			else:
				templates.insert(0, 'home.%s' % extension)
				templates.insert(0, '%s/home.%s' % (request.network.domain, extension))
				body_classes.append('home')
				
				if request.user.is_authenticated():
					user_streams = request.user.streams.filter(
						part_of__network = request.network
					)
		
		stream = None
		stream_tags = None
		reporters = None
		
		if request.profile:
			title_parts.insert(0, request.profile.get_full_name() or request.profile.username)
	
	if category:		
		posts = posts.filter(stream__part_of__category = category)
		related_streams = category.streams.public()
		
		if stream:
			if request.profile:
				related_streams = related_streams.exclude(
					pk = stream.part_of.pk
				)
			else:
				related_streams = related_streams.exclude(
					pk = stream.pk
				)
	
	if related_streams and coords:
		related_streams = related_streams.near(*coords)
	
	stream_tags_dict = {}
	if stream_tags:
		for (domain, tag) in stream_tags.values_list('domain', 'tag'):
			key = domain.replace('.', '__')
			tag_list = stream_tags_dict.get(key, [])
			
			if not tag in tag_list:
				tag_list.append(tag)
			
			stream_tags_dict[key] = tag_list
	
	post_types = posts.all().distinct().values_list('kind', flat = True)
	post_types.query.group_by = ['kind']
	
	if kind:
		posts = posts.all().filter(kind = kind)
	
	if request.is_ajax():
		templates = 'posts.inc.html'
	
	since_id = None
	if request.GET.get('since'):
		try:
			posts = posts.filter(
				pk__gt = request.GET.get('since')
			)
			
			since_id = request.GET.get('since')
		except ValueError:
			pass
	
	posts.filter(
		state = POST_CONVERTING,
		posted__lte = datetime.now() - timedelta(hours = 3)
	).delete()
	
	not_live = posts.exclude(state = POST_LIVE)
	if not_live.count() > 0:
		posts = posts.all().live().filter(pk__lt = not_live[0].pk)
	else:
		posts = posts.live()
	
	paginator = Paginator(posts, page_size)
	
	try:
		page = paginator.page(
			request.GET.get('page', 1)
		)
	except PageNotAnInteger:
		page = paginator.page(1)
	except EmptyPage:
		return HttpResponseRedirect(
			'?page=%d' % paginator.num_pages
		)
	
	if posts.count() > 0:
		latest_id = posts.all().values_list('pk', flat = True).order_by('-pk')[0]
	else:
		latest_id = None
	
	if request.is_ajax() and 'text/javascript' in request.META.get('HTTP_ACCEPT'):
		templates = 'posts.inc.js'
	
	if can_post:
		body_classes.append('post-form')
	
	def container_id():
		if request.GET.get('container'):
			return request.GET['container']
		
		import random, string
		
		return ''.join(
			random.sample(string.letters + string.digits, 10)
		)
	
	return TemplateResponse(
		request,
		templates,
		{
			'posts': page,
			'stream': stream,
			'other_streams': other_streams,
			'stream_tags': stream_tags_dict,
			'category': category,
			'related_streams': related_streams,
			'reporters': reporters,
			'post_types': post_types.all(),
			'selected_post_type': kind,
			'latest_id': latest_id,
			'since_id': since_id,
			'body_classes': body_classes,
			'title_parts': title_parts,
			'post_form': can_post and PostForm() or None,
			'container_id': format == 'embed' and container_id() or None,
			'iframe': format == 'iframe',
			'user_streams': user_streams
		},
		mimetype = mimetype
	)

def post(request, stream, pk, format = 'standard'):
	stream = get_object_or_404(
		UserStream,
		part_of__slug = stream,
		part_of__network = request.network,
		profile = request.profile
	)
	
	post = get_object_or_404(Post, stream = stream, pk = pk, state = POST_LIVE)
	if post.sets.count() > 0:
		title = post.sets.all()[0].text or post.text
	else:
		title = post.text
	
	if format == 'embed':
		templates = 'streams/post.embed.html'
	else:
		templates = (
			'streams/profile/post.html',
			'streams/post.html'
		)
	
	return TemplateResponse(
		request,
		templates,
		{
			'post': post,
			'stream': stream,
			'title_parts': (
				title, post.author.get_full_name() or post.author.username,
				stream.part_of.name
			)
		}
	)

def set(request, stream, pk):
	stream = get_object_or_404(UserStream,
		part_of__slug = stream,
		part_of__network = request.network,
		profile = request.profile
	)
	
	sett = get_object_or_404(Set, stream = stream, pk = pk)
	
	return TemplateResponse(
		request,
		(
			'streams/profile/set.html',
			'streams/set.html'
		),
		{
			'set': sett,
			'stream': stream,
			'body_classes': ('streams', 'set'),
			'title_parts': (
				sett.text or '%s collection' % sett.get_kind_display(), stream.part_of.name
			)
		}
	)

@login_required
def create(request):
	from django.db.models import Q
	
	alt_streams = []
	if request.method == 'GET':
		form = UserStreamForm(user = request.user, network = request.network)
	else:
		form = UserStreamForm(user = request.user, network = request.network, data = request.POST)
		
		if form.is_valid():
			tags = [form.cleaned_data['slug'].lower()]
			if form.cleaned_data.get('twitter'):
				tags.append(form.cleaned_data['twitter'].lower())
			
			if form.cleaned_data.get('flickr'):
				tags.append(form.cleaned_data['flickr'].lower())
			
			q = Q(slug__in = tags) | Q(tags__tag__in = tags)
			alt_streams = Stream.objects.filter(q).distinct()
			
			if alt_streams.count() == 0:
				stream = form.save()
				
				messages.add_message(
					request,
					messages.SUCCESS,
					u'Your new stream is alive and kicking!'
				)
				
				return HttpResponseRedirect(
					'http://%s.%s%s' % (
						request.user.username,
						request.network.domain,
						stream.get_absolute_url()
					)
				)
	
	classes = ('create-post',)
	if alt_streams and any(alt_streams):
		classes += ('alt-streams',)
	
	return TemplateResponse(
		request,
		(
			'%s/streams/create.html' % (request.network.domain),
			'streams/create.html'
		),
		{
			'alt_streams': alt_streams,
			'form': form,
			'body_classes': classes,
			'title_parts': ('Create a new stream',)
		}
	)

@login_required
def join(request, slug):
	stream = get_object_or_404(Stream, network = request.network, slug__iexact = slug)
	
	try:
		stream = UserStream.objects.get(
			profile = request.user,
			part_of = stream
		)
		
		messages.add_message(
			request,
			messages.INFO,
			u'You have already created this stream.'
		)
	except UserStream.DoesNotExist:
		stream = UserStream.objects.create(
			profile = request.user,
			part_of = stream
		)
		
		for tag in stream.part_of.tags.filter(
			domain = 'twitter.com').values_list('tag', flat = True
		)[:1]:
			stream.part_of.tags.create(
				user = request.user,
				domain = 'twitter.com',
				tag = tag
			)
		
		for tag in stream.part_of.tags.filter(
			domain = 'flickr.com').values_list('tag', flat = True
		)[:1]:
			stream.part_of.tags.create(
				user = request.user,
				domain = 'flickr.com',
				tag = tag
			)
		
		messages.add_message(
			request,
			messages.SUCCESS,
			u'Your new stream is ready. Go forth and tell your story!'
		)
	
	return HttpResponseRedirect(
		stream.get_full_base_url()
	)

@login_required
def edit(request, slug):
	stream = get_object_or_404(UserStream,
		profile = request.user,
		part_of__slug = slug,
		part_of__network = request.network
	)
	
	if request.method == 'GET':
		form = UserStreamForm(
			user = request.user,
			network = request.network,
			instance = stream
		)
	else:
		form = UserStreamForm(
			data = request.POST,
			user = request.user,
			network = request.network,
			instance = stream
		)
		
		if form.is_valid():
			stream = form.save()
			
			messages.add_message(
				request,
				messages.SUCCESS,
				u'Your stream has been updated.'
			)
			
			return HttpResponseRedirect(
				stream.get_full_base_url()
			)
	
	return TemplateResponse(
		request,
		(
			'%s/streams/edit.html' % (request.network.domain),
			'streams/edit.html',
		),
		{
			'stream': stream,
			'form': form,
			'body_classes': ('streams', 'edit'),
			'title_parts': ('Edit', stream.part_of.name)
		}
	)

@login_required
def embed(request, slug):
	stream = get_object_or_404(UserStream,
		profile = request.user,
		part_of__slug = slug,
		part_of__network = request.network
	)
	
	if not request.profile:
		return HttpResponseRedirect(
			'http://%s.%s%s' % (
				request.user.username,
				request.network.domain,
				reverse('embed_stream_options', args = [slug])
			)
		)
	
	form = StreamEmbedForm(request.POST or None, instance = stream)
	if request.method == 'POST' and form.is_valid():
		form.save()
		form = StreamEmbedForm(instance = stream)
	
	if Profile.objects.filter(user = request.user).count() == 0:
		Profile.objects.create(user = request.user)
	
	return TemplateResponse(
		request,
		(
			'%s/streams/embed.html' % (request.network.domain),
			'streams/embed.html'
		),
		{
			'stream': stream,
			'form': form,
			'body_classes': ('streams', 'embed'),
			'title_parts': ('Embed', stream.part_of.name),
			'embeds': stream.embeds.all()
		}
	)

@login_required
def leave(request, slug):
	stream = get_object_or_404(UserStream,
		profile = request.user,
		part_of__slug = slug,
		part_of__network = request.network
	)
	
	if stream.part_of.contributors.count() > 1:
		stream.delete()
		messages.add_message(
			request,
			messages.SUCCESS,
			u'You have left this stream.'
		)
	else:
		stream.part_of.delete()
		messages.add_message(
			request,
			messages.SUCCESS,
			u'This stream has been successfully deleted.'
		)
	
	return HttpResponseRedirect('/')