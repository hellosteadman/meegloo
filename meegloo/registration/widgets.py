#!/usr/bin/env python
# encoding: utf-8

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _
import os

class DeleteCheckboxWidget(forms.CheckboxInput):
	def __init__(self, *args, **kwargs):
		self.is_image = kwargs.pop('is_image')
		self.value = kwargs.pop('initial')
		super(DeleteCheckboxWidget, self).__init__(*args, **kwargs)
	
	def render(self, name, value, attrs=None):
		value = value or self.value
		if value:
			s = u'<label for="%s">%s %s</label>' % (
				attrs['id'],
				super(DeleteCheckboxWidget, self).render(name, False, attrs),
				_('Delete this image')
			)
			
			if self.is_image:
				s += u'<br><img src="%s%s" width="50">' % (settings.MEDIA_URL, value)
			else:
				s += u'<br><a href="%s%s">%s</a>' % (settings.MEDIA_URL, value, os.path.basename(value))
			
			return s
		else:
			return u''

class RemovableFileFormWidget(forms.MultiWidget):
	def __init__(self, is_image=False, initial=None, **kwargs):
		widgets = (forms.FileInput(), DeleteCheckboxWidget(is_image=is_image, initial=initial))
		super(RemovableFileFormWidget, self).__init__(widgets)
	
	def decompress(self, value):
		return [None, value]

class RemovableFileFormField(forms.MultiValueField):
	widget = RemovableFileFormWidget
	field = forms.FileField
	is_image = False

	def __init__(self, *args, **kwargs):
		fields = [self.field(*args, **kwargs), forms.BooleanField(required=False)]
		# Compatibility with form_for_instance
		if kwargs.get('initial'):
			initial = kwargs['initial']
		else:
			initial = None
		self.widget = self.widget(is_image=self.is_image, initial=initial)
		super(RemovableFileFormField, self).__init__(fields, label=kwargs.pop('label'), required=False)

	def compress(self, data_list):
		return data_list

class RemovableImageFormField(RemovableFileFormField):
	field = forms.ImageField
	is_image = True