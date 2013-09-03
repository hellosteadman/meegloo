#!/usr/bin/env python
# encoding: utf-8

# -*- coding: utf-8 -*-
#
# Blackbirdpy - a Python implementation of Blackbird Pie, the tool
# @robinsloan uses to generate embedded HTML tweets for blog posts.
#
# See: http://media.twitter.com/blackbird-pie
#
# This Python version was written by Jeff Miller, http://twitter.com/jeffmiller
#
# Requires Python 2.6.
#
# Usage:
#
# - To generate embedded HTML for a tweet from inside a Python program:
#
#   import blackbirdpy
#   embed_html = blackbirdpy.embed_tweet_html(tweet_url)
#
# - To generate embedded HTML for a tweet from the command line:
#
#   $ python blackbirdpy.py <tweeturl>
#	 e.g.
#   $ python blackbirdpy.py http://twitter.com/punchfork/status/16342628623
#
# - To run unit tests from the command line:
#
#   $ python blackbirdpy.py --unittest

import datetime, email.utils, re, unittest, urllib2
from django.utils import simplejson
from django.template.loader import render_to_string

def wrap_user_mention_with_link(text):
	"""Replace @user with <a href="http://twitter.com/user">@user</a>"""
	return re.sub(r'(^|[^\w])@(\w+)\b', r'\1<a href="http://twitter.com/\2">@\2</a>', text)

def wrap_hashtag_with_link(text):
	"""Replace #hashtag with <a href="http://twitter.com/search?q=hashtag">#hashtag</a>"""
	return re.sub(r'(^|[^\w])#(\w+)\b', r'\1<a href="http://twitter.com/search?q=\2">#\2</a>', text)

def wrap_http_with_link(text):
	"""Replace http://foo with <a href="http://foo">http://foo</a>"""
	return re.sub(r'(^|[^\w])(http://[^\s]+)', r'\1<a href="\2">\2</a>', text)

def timestamp_string_to_datetime(text):
	"""Convert a string timestamp of the form 'Wed Jun 09 18:31:55 +0000 2010'
	into a Python datetime object."""
	tm_array = email.utils.parsedate_tz(text)
	return datetime.datetime(*tm_array[:6]) - datetime.timedelta(seconds=tm_array[-1])

def easy_to_read_timestamp_string(dt):
	"""Convert a Python datetime object into an easy-to-read timestamp
	string, like '1:33 PM Wed Jun 16, 2010'."""
	return re.sub(r'(^| +)0', r'\1', dt.strftime('%I:%M %p %a %b %d, %Y'))

def tweet_id_from_tweet_url(tweet_url):
	"""Extract and return the numeric tweet ID from a full tweet URL."""
	match = re.match(r'^https?://twitter\.com/(#!/)?\w+/status(?:es)?/(?P<id>\d+)', tweet_url)
	
	try:
		return match.groupdict()['id']
	except:
		raise ValueError('Invalid tweet URL: %s' % tweet_url)

def embed_tweet_html(tweet_url, extra_css = None):
	"""Generate embedded HTML for a tweet, given its Twitter URL.  The
	result is formatted in the style of Robin Sloan's Blackbird Pie.
	See: http://media.twitter.com/blackbird-pie
	
	The optional extra_css argument is a dictionary of CSS class names
	to CSS style text.  If provided, the extra style text will be
	included in the embedded HTML CSS.  Currently only the bbpBox
	class name is used by this feature.
	"""
	
	tweet_id = tweet_id_from_tweet_url(tweet_url)
	api_url = 'http://api.twitter.com/1/statuses/show.json?id=' + tweet_id
	
	try:
		request = urllib2.Request(
			api_url, headers = {
				'Accept': 'application/json',
				'User-Agent': 'Meegloo/oembed'
			}
		)
		
		api_handle = urllib2.urlopen(request)
	except:
		return ''
	
	api_data = api_handle.read()
	api_handle.close()
	tweet_json = simplejson.loads(api_data)

	tweet_text = wrap_user_mention_with_link(
		wrap_hashtag_with_link(
			wrap_http_with_link(
				tweet_json['text'].replace('\n', ' ')
				)
			)
		)

	tweet_created_datetime = timestamp_string_to_datetime(tweet_json["created_at"])
	tweet_local_datetime = tweet_created_datetime + (datetime.datetime.now() - datetime.datetime.utcnow())
	tweet_easy_timestamp = easy_to_read_timestamp_string(tweet_local_datetime)

	if extra_css is None:
		extra_css = {}
	
	return render_to_string(
		'oembed/blackbird.inc.html',
		{
			'url': tweet_url,
			'screen_name': tweet_json['user']['screen_name'],
			'real_name': tweet_json['user']['name'],
			'text': tweet_text,
			'source': tweet_json['source'],
			'profile_image': tweet_json['user']['profile_image_url'],
			'profile_background_colour': tweet_json['user']['profile_background_color'],
			'profile_background_image': tweet_json['user']['profile_background_image_url'],
			'profile_text_colour': tweet_json['user']['profile_text_color'],
			'profile_link_colour': tweet_json['user']['profile_link_color'],
			'timestamp': tweet_json['created_at'],
			'easy_timestamp': tweet_easy_timestamp,
			'utc_offset': tweet_json['user']['utc_offset'],
			'extra_css': extra_css.get('bbpBox', '')
		}
	)