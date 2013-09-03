#!/usr/bin/env python
# encoding: utf-8

from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^admin/', include(admin.site.urls)),
	url(r'^api/', include('meegloo.api.urls')),
	url(r'^uploadify/', include('meegloo.uploadify.urls')),
	url(r'^oembed/', include('meegloo.oembed.urls')),
	url(r'^about/$', 'django.views.generic.simple.direct_to_template',
		{
			'template': 'pages/about.html',
			'extra_context': {
				'body_classes': ('about', 'page'),
				'title_parts': ('About Meegloo',)
			}
		}, name = 'about'
	),
	url(r'^about/streams/$', 'django.views.generic.simple.direct_to_template',
		{
			'template': 'pages/streams.html',
			'extra_context': {
				'body_classes': ('about-streams', 'about', 'page'),
				'title_parts': ('Streams', 'About Meegloo',)
			}
		}, name = 'about_streams'
	),
	url(r'^about/networks/$', 'django.views.generic.simple.direct_to_template',
		{
			'template': 'pages/networks.html',
			'extra_context': {
				'body_classes': ('about-networks', 'about', 'page'),
				'title_parts': ('Networks', 'About Meegloo',)
			}
		}, name = 'about_networks'
	),
	url(r'^badges/$', 'django.views.generic.simple.direct_to_template',
		{
			'template': 'pages/badges.html',
			'extra_context': {
				'body_classes': ('badges', 'page'),
				'title_parts': ('Badges',)
			}
		}, name = 'badges'
	),
	url(r'^downloads/$', 'django.views.generic.simple.direct_to_template',
		{
			'template': 'pages/downloads.html',
			'extra_context': {
				'body_classes': ('downloads', 'page'),
				'title_parts': ('Downloads',)
			}
		}, name = 'downloads'
	),
	url(r'^terms/$', 'django.views.generic.simple.direct_to_template',
		{
			'template': 'pages/terms.html',
			'extra_context': {
				'body_classes': ('terms', 'page'),
				'title_parts': ('Terms and conditions',)
			}
		}, name = 'terms'
	),
	url(r'^privacy/$', 'django.views.generic.simple.direct_to_template',
		{
			'template': 'pages/privacy.html',
			'extra_context': {
				'body_classes': ('privacy', 'page'),
				'title_parts': ('Privacy policy',)
			}
		}, name = 'privacy'
	),
	url(r'^terms/mobile/$', 'django.views.generic.simple.direct_to_template',
		{
			'template': 'pages/terms.mobile.html'
		}, name = 'terms_mobile'
	),
	url(r'^social/', include('meegloo.social.urls')),
	url(r'^mail/', include('meegloo.mail.urls')),
	url(r'^', include('meegloo.viral.urls')),
	url(r'^', include('meegloo.core.urls')),
	url(r'^', include('meegloo.registration.urls')),
	url(r'^', include('meegloo.networks.urls')),
	url(r'^', include('meegloo.streams.urls'))
)

if getattr(settings, 'DEBUG', False):
	urlpatterns += patterns('django.views.static',
		(r'^media/(?P<path>.+)$', 'serve',
			{
				'document_root': getattr(settings, 'MEDIA_ROOT')
			}
		)
	)
	
	urlpatterns += patterns('django.views.generic.simple',
		(r'404\.html$', 'direct_to_template',
			{
				'template': '404.html'
			}
		)
	)
	
	urlpatterns += patterns('django.views.generic.simple',
		(r'500\.html$', 'direct_to_template',
			{
				'template': '500.html'
			}
		)
	)