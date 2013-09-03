#!/usr/bin/env python
# encoding: utf-8

from django import forms
from django.conf import settings
from meegloo.streams.models import Stream, UserStream, Category, Post
from meegloo.streams.helpers import clean_domain
from uuid import uuid4

class PostForm(forms.ModelForm):
	attachment = forms.FileField(required = False)
	geotag = forms.BooleanField(required = False)
	latitude = forms.CharField(widget = forms.HiddenInput, required = False)
	longitude = forms.CharField(widget = forms.HiddenInput, required = False)
	
	def __init__(self, *args, **kwargs):
		super(PostForm, self).__init__(*args, **kwargs)
		self.fields['text'].widget = forms.Textarea()
		self.fields['kind'].widget = forms.HiddenInput()
		self.fields['kind'].initial = 'text'
		self.fields['guid'].widget = forms.HiddenInput()
		self.fields['guid'].initial = str(uuid4())
	
	class Meta:
		model = Post
		fields = ('text', 'kind', 'guid', 'tweet', 'geotag', 'latitude', 'longitude')

class UserStreamForm(forms.Form):
	name = forms.CharField(
		max_length = 50, label = u'Stream name',
		help_text = 'This shows at the top of your stream page'
	)
	
	slug = forms.RegexField(
		max_length = 20, label = 'Stream URL', regex = r'^[\w-]+$', error_messages = {
			'invalid': 'The URL should contain only letters, numbers and hypens'
		}, help_text = u'This forms part of your stream URL (ie: http://%s.meegloo.com/yourstream)'
	)
	
	description = forms.CharField(
		max_length = 200, required = False, widget = forms.Textarea,
		help_text = u'Tell us a little about the topic or event, and how you&rsquo;ll be covering it'
	)
	
	category = forms.ModelChoiceField(
		queryset = Category.objects.all(), initial = 5,
		help_text = u'Help make your stream easier to find'
	)
	
	private = forms.BooleanField(
		label = u'Make my coverage private', required = False,
		help_text = u'That way, only people you give the address of the feed to will see it'
	)
	
	twitter_hashtag = forms.RegexField(
		max_length = 30, required = False, help_text = u'This tag will be appended to all your ' \
		'tweets on this topic, and helps people find and contribute to your stream',
		regex = r'^#?[\w]+$'
	)
	
	flickr_tag = forms.RegexField(
		max_length = 30, required = False, help_text = u'Flickr photos are displayed alongside tweets ' \
		'in your stream', regex = r'^[\w]+$', error_messages = {
			'invalid': 'Please enter a lowercase tag without spaces'
		}
	)
	
	def clean_slug(self):
		slug = self.cleaned_data.get('slug')
		
		if slug.lower() in getattr(settings, 'INVALID_SLUGS', []):
			raise forms.ValidationError('Sorry, that URL is reserved')
		
		return slug
	
	def __init__(self, user, network, instance = None, *args, **kwargs):
		super(UserStreamForm, self).__init__(*args, **kwargs)
		
		self.user = user
		self.network = network
		
		if instance:
			self.instance = instance
			
			if self.instance.part_of.contributors.count() > 1:
				del self.fields['name']
				del self.fields['slug']
				del self.fields['description']
				del self.fields['category']
			else:
				self.fields['name'].initial = self.instance.part_of.name
				self.fields['slug'].initial = self.instance.part_of.slug
				self.fields['category'].initial = self.instance.part_of.category
			
			twitter_tags = self.instance.part_of.tags.filter(
				domain = 'twitter.com',
				user = self.user
			)
			
			if twitter_tags.count() > 0:
				self.fields['twitter_hashtag'].initial = twitter_tags[0].tag
			
			flickr_tags = self.instance.part_of.tags.filter(
				domain = 'flickr.com',
				user = self.user
			)
			
			if flickr_tags.count() > 0:
				self.fields['flickr_tag'].initial = flickr_tags[0].tag
			
			self.fields['private'].initial = self.instance.private
		else:
			self.instance = None
	
	def save(self, commit = False):
		twitter_hashtag = self.cleaned_data.get('twitter_hashtag')
		flickr_tag = self.cleaned_data.get('flickr_tag')
		
		if twitter_hashtag and twitter_hashtag.startswith('#'):
			twitter_hashtag = twitter_hashtag[1:]
		
		if not self.instance:
			stream = Stream.objects.create(
				name = self.cleaned_data['name'],
				slug = self.cleaned_data['slug'].lower(),
				description = self.cleaned_data.get('description'),
				category = self.cleaned_data.get('category'),
				network = self.network
			)
			
			if twitter_hashtag:
				stream.tags.create(
					user = self.user,
					domain = 'twitter.com',
					tag = twitter_hashtag.lower()
				)
			
			if flickr_tag:
				stream.tags.create(
					user = self.user,
					domain = 'flickr.com',
					tag = flickr_tag
				)
			
			return UserStream.objects.create(
				part_of = stream,
				profile = self.user,
				private = self.cleaned_data.get('private')
			)
		else:
			if self.cleaned_data.get('name'):
				self.instance.part_of.name = self.cleaned_data['name']
			
			if self.cleaned_data.get('description'):
				self.instance.part_of.description = self.cleaned_data.get('description')
			
			if self.cleaned_data.get('category'):
				self.instance.part_of.category = self.cleaned_data.get('category')
			
			self.instance.private = self.cleaned_data.get('private')
			self.instance.part_of.save()
			self.instance.save()
			
			if twitter_hashtag:
				self.instance.part_of.tags.get_or_create(
					user = self.user,
					domain = 'twitter.com',
					tag = twitter_hashtag.lower()
				)
			else:
				self.instance.part_of.tags.filter(
					user = self.user,
					domain = 'twitter.com'
				).delete()
			
			if flickr_tag:
				self.instance.part_of.tags.get_or_create(
					user = self.user,
					domain = 'flickr.com',
					tag = flickr_tag.lower()
				)
			else:
				self.instance.part_of.tags.filter(
					user = self.user,
					domain = 'flickr.com',
				).delete()
				
			return self.instance
			
class StreamEmbedForm(forms.Form):
	domains = forms.CharField(
		widget = forms.Textarea(
			attrs = {
				'placeholder': 'myeventwebsite.com'
			}
		),
		required = False
	)
	
	def __init__(self, *args, **kwargs):
		self.instance = kwargs.pop('instance', None)
		super(StreamEmbedForm, self).__init__(*args, **kwargs)
		
		self.fields['domains'].initial = '\n'.join(
			self.instance.embeds.values_list('domain', flat = True)
		)
	
	def clean_domains(self):
		import re
		
		ex = re.compile(r'^(?P<domain>[a-zA-z0-9\.]+)(?P<port>\:\d+)?$')
		domains = self.cleaned_data.get('domains')
		d = []
		
		if domains:
			for (i, domain) in enumerate(domains.splitlines()):
				if domain:
					try:
						domain = clean_domain(domain)
					except:
						raise forms.ValidationError(
							u'Line %d contains something that doesn\'t look like a domain name' % (i + 1)
						)
		
		d = '\n'.join(d)
		self.cleaned_data['domains'] = d
		return d
	
	def save(self):
		domains = self.cleaned_data.get('domains')
		
		if domains:
			domains = domains.split('\n')
			self.instance.embeds.exclude(domain__in = domains).delete()
			for domain in domains:
				if self.instance.embeds.filter(domain__iexact = domain).count() == 0:
					self.instance.embeds.create(domain = domain)
		else:
			self.instance.embeds.all().delete()