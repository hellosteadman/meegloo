#!/usr/bin/env python
# encoding: utf-8

from django.http import HttpResponseBadRequest, Http404
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db.models import Count
from django.template.loader import render_to_string
from django.template import RequestContext
from django.contrib.contenttypes.models import ContentType
from piston.handler import BaseHandler
from piston.utils import rc
from meegloo.api.helpers import format_errors
from meegloo.streams import POST_LIVE, POST_TYPES, POST_CONVERTING
from meegloo.streams.models import Post, Media, UserStream
from meegloo.social.models import Comment, Question, Answer, Poll, PollAnswer
from tempfile import mkstemp
import logging, os, mimetypes

def add_media(stream, results):
	for res in results:
		if res['kind'] in ('photo', 'video'):
			res['thumbnail'] = '%s/posts/%d.png' % (
				stream, res['id']
			)
		
		if res['kind'] == 'audio':
			try:
				res['mp3'] = Media.objects.get(
					post__pk = res['id'],
					mimetype__in = ('audio/mp3', 'audio/mpeg')
				).content.url
			except Media.DoesNotExist:
				pass
		elif res['kind'] == 'video':
			try:
				res['mp4'] = Media.objects.get(
					post__pk = res['id'],
					mimetype = 'video/mp4'
				).content.url
			except Media.DoesNotExist:
				pass
	
	return results

def add_url(stream, results):
	for res in results:
		res['url'] = '%s/posts/%d.html' % (
			stream, res['id']
		)
	
	return results

class PostHandler(BaseHandler):
	model = Post
	exclude = ('_state', 'stream')
	
	def update(self, request, stream, id):
		pass
	
	def read(self, request, stream, id = None, **kwargs):
		if id:
			result = get_object_or_404(Post,
				stream__part_of__slug = stream,
				stream__part_of__network = request.network,
				state = POST_LIVE,
				pk = id
			)
			
			context = RequestContext(request)
			context['post'] = result
			
			result = {
				'kind': result.kind,
				'application': result.application and result.application.name or '',
				'id': result.pk,
				'posted': result.posted,
				'text': result.text,
				'author': result.author,
				'location': result.area,
				'url': '%s/posts/%d.html' % (
					stream, result.pk
				),
				'media': result.media.values('mimetype', 'content'),
				'comments': [
					{
						'text': text,
						'posted': posted,
						'author': author
					} for text, posted, author in result.comments.values_list(
						'text', 'posted', 'author__username'
					)[:10]
				],
				'html': render_to_string(
					'api/post.html',
					context
				)
			}
			
			return result
		
		result = super(PostHandler, self).read(
			request,
			stream__part_of__slug = stream,
			stream__part_of__network = request.network,
			state = POST_LIVE,
			**kwargs
		).annotate(
			comment_count = Count('comments')
		)
		
		if 'kind' in request.GET:
			if not request.GET.get('kind') in [x for (x, y) in POST_TYPES]:
				return HttpResponseBadRequest('Unknown post type "%s"' % request.GET.get('kind'))
			
			result = result.filter(
				kind = request.GET['kind']
			)
		
		if 'author' in request.GET:
			result = result.filter(
				author__username = request.GET['author']
			)
		
		if request.GET.get('since'):
			try:
				result = result.filter(
					pk__gt = int(request.GET.get('since'))
				)
			except ValueError:
				pass
		
		result = result.values(
			'kind', 'application__name',
			'id', 'posted', 'text', 'author__username', 'comment_count'
		)
		
		try:
			rpp = int(request.GET.get('rpp', 100))
		except TypeError, ValueError:
			return HttpResponseBadRequest('Invalid rpp value')
		
		try:
			page = int(request.GET.get('page', 1))
		except TypeError, ValueError:
			return HttpResponseBadRequest('Invalid page value')
		
		paginator = Paginator(result, rpp)
		
		try:
			result = add_media(
				stream, add_url(
					stream, paginator.page(page).object_list
				)
			)
		except (InvalidPage, EmptyPage):
			result = []
		
		for res in result:
			res['author'] = res.pop('author__username')
			res['comments'] = res.pop('comment_count')
		
		return result
	
	def create(self, request, stream):
		from datetime import datetime
		
		stream = get_object_or_404(
			UserStream,
			part_of__slug = stream,
			part_of__network = request.network,
			profile = request.user
		)
		
		if not request.POST.get('kind') in [x for (x, y) in POST_TYPES]:
			return HttpResponseBadRequest('Unknown post type "%s"' % request.POST.get('kind'))
		
		logger = logging.getLogger('api')
		logger.debug('Creating post')
		
		post = Post(
			stream = stream,
			author = request.user,
			application = request.consumer,
			kind = request.POST.get('kind'),
			text = request.POST.get('text'),
			longitude = request.POST.get('lon'),
			latitude = request.POST.get('lat'),
			posted = datetime.now()
		)
		
		if request.POST.get('tags'):
			tags = request.POST.get('tags').replace(',', ' ')
			while tags.find('  ') > 01:
				tags = tags.replace('  ', ' ')
		else:
			tags = ''
		
		if request.POST.get('coords'):
			try:
				post.latitude, post.longitude = request.POST.get('coords').split(',')
			except:
				return HttpResponseBadRequest('Latitude and longitude not specified correctly')
		
		post.tweet = request.POST.get('tweet', 'false') == 'true'
		if post.tweet:
			logger.debug('Tweeting is %s' % request.POST.get(
				'tweet', 'false'
			) == 'true' and 'on' or 'off'
		)
		
		if request.FILES and request.FILES['media'] and request.POST.get('kind') in ('audio', 'video'):
			# This is a media post. We need to convert the media after we save the post,
			# so we can feed back to the API user that the post was submitted successfully
			# without keeping them on the line
			
			post.state = POST_CONVERTING
			logger.debug('Preparing to convert %s' % request.POST.get('kind'))
			
			try:
				post.full_clean()
				post.save(tags = tags)
				
				media = request.FILES['media']
				handle, filename = mkstemp('.tmp',
					dir = getattr(settings, 'TEMP_DIR')
				)
				
				try:
					os.write(handle, media.read())
				finally:
					os.close(handle)
				
				conversion = post.conversions.create(
					name = media.name,
					state = u'Started'
				)
				
				conversion.start(filename)
				return post
			except ValidationError, ex:
				return HttpResponseBadRequest(
					format_errors(ex)
				)
		
		elif request.FILES and request.FILES['media'] and request.POST.get('kind') == 'photo':
			from django.core.files import File
			
			logger.debug('Preparing to convert %s' % request.POST.get('kind'))
			
			try:
				post.state = POST_LIVE
				post.full_clean()
				post.save(tags = tags)
				
				f = request.FILES['media']
				dest_handle, dest_name = mkstemp(
					os.path.splitext(f.name)[-1]
				)
				
				try:
					os.write(dest_handle, f.read())
				finally:
					os.close(dest_handle)
				
				mime, encoding = mimetypes.guess_type(dest_name)
				f = open(dest_name, 'r')
				
				try:
					post.media.create(
						mimetype = mime,
						content = File(f, name = dest_name)
					)
				finally:
					f.close()
				
				if post.tweet:
					post.update_twitter()
				
				return post
			except ValidationError, ex:
				return HttpResponseBadRequest(
					format_errors(ex)
				)
		
		elif request.POST.get('kind') == 'text':
			# This is a standard text-based post, so we can just save it and feed back to
			# the API user the details of the new post
			
			try:
				post.full_clean()
				post.save(tags = tags)
				
				if post.tweet:
					post.update_twitter()
				
				return post
			except ValidationError, ex:
				return HttpResponseBadRequest(
					format_errors(ex)
				)
		else:
			return []
		
		return HttpResponseBadRequest(form.errors[0])
	
	def delete(self, request, stream, id):
		self.queryset(request).get(
			stream__part_of__slug = stream,
			pk = id
		).delete()
		
		return rc.DELETED

class MyPostHandler(BaseHandler):
	allowed_methods = ('GET',)
	exclude = ('_state', 'stream')
	
	def read(self, request, stream):
		result = Post.objects.filter(
			stream__part_of__slug = stream,
			stream__part_of__network = request.network,
			author = request.user
		).values(
			'kind', 'application__name',
			'id', 'posted', 'text', 'author__username'
		)
		
		try:
			rpp = int(request.GET.get('rpp', 100))
		except TypeError, ValueError:
			return HttpResponseBadRequest('Invalid rpp value')
		
		try:
			page = int(request.GET.get('page', 1))
		except TypeError, ValueError:
			return HttpResponseBadRequest('Invalid page value')
		
		paginator = Paginator(result, rpp)
		
		try:
			result = add_media(
				stream, add_url(stream, paginator.page(page).object_list)
			)
		except (InvalidPage, EmptyPage):
			result = []
		
		return result

class PostCommentHandler(BaseHandler):
	def read(self, request, stream, id):
		post = Post.objects.get(
			stream__part_of__slug = stream,
			stream__part_of__network = request.network,
			pk = id
		)
		
		comments = [
			{
				'id': comment.pk,
				'text': comment.text,
				'posted': comment.posted,
				'author': comment.author
			} for comment in post.comments.all()[:10]
		]
		
		return comments
	
	def create(self, request, stream, id):
		post = Post.objects.get(
			stream__part_of__slug = stream,
			stream__part_of__network = request.network,
			pk = id
		)
		
		comment = post.comments.create(
			text = request.POST['text'],
			tweet = request.POST.get('tweet', 'false') == 'true',
			network = request.network,
			author = request.user
		)
		
		return {
			'id': comment.pk,
			'text': comment.text,
			'posted': comment.posted,
			'author': comment.author
		}

class PostAnswerHandler(BaseHandler):
	def read(self, request, stream, id):
		post = Post.objects.get(
			stream__part_of__slug = stream,
			stream__part_of__network = request.network,
			pk = id
		)
		
		answers = [
			{
				'id': answer.pk,
				'text': answer.text,
				'answered': answer.answered,
				'user': answer.user
			} for answer in Answer.objects.filter(
				question__content_type = ContentType.objects.get_for_model(post),
				question__object_id = post.pk
			)
		]
		
		return answers
	
	def create(self, request, stream, id):
		post = Post.objects.get(
			stream__part_of__slug = stream,
			stream__part_of__network = request.network,
			pk = id
		)
		
		answer = request.POST.get('answer')
		
		if not answer:
			return HttpResponseBadRequest('answer required')
		
		try:
			question = Poll.objects.get(
				content_type = ContentType.objects.get_for_model(post),
				object_id = post.pk
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
			
			answer = PollAnswer.objects.create(
				question = question,
				option = option,
				text = option.label,
				user = request.user
			)
		
		except Poll.DoesNotExist:
			question = Question.objects.get(
				content_type = ContentType.objects.get_for_model(post),
				object_id = post.pk
			)
			
			answer = question.answers.create(
				user = request.user,
				text = answer
			)
		except Question.DoesNotExist:
			raise Http404()
		
		return {
			'id': answer.pk,
			'text': answer.text,
			'answered': answer.answered,
			'user': answer.user
		}