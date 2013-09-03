#!/usr/bin/env python
# encoding: utf-8

from django import forms
from meegloo.social.models import Comment

class CommentForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(CommentForm, self).__init__(*args, **kwargs)
		
		self.fields['text'].widget.attrs['placeholder'] = 'Post your comment here'
		if self.instance.author.oauth_tokens.filter(site = 'twitter').count() == 0:
			del self.fields['tweet']
		else:
			self.fields['tweet'].label = u'Post this comment to Twitter'
	
	class Meta:
		model = Comment
		fields = ('text', 'tweet')