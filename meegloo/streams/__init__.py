#!/usr/bin/env python
# encoding: utf-8

POST_TYPES = (
	(u'text', u'text'),
	(u'photo', u'photo'),
	(u'audio', u'audio'),
	(u'video', u'video'),
	(u'url', u'URL'),
	(u'slide', u'slideshow'),
	(u'question', u'Question'),
	(u'poll', u'Poll')
)

POST_CONVERSION_FAILED = -2
POST_DELETING = -1
POST_CONVERTING = 0
POST_UPLOADING = 1
POST_LIVE = 2

POST_STATES = (
	(POST_CONVERSION_FAILED, 'Conversion failed'),
	(POST_DELETING, 'Deleting'),
	(POST_CONVERTING, 'Converting'),
	(POST_UPLOADING, 'Uploading'),
	(POST_LIVE, 'Live')
)