#!/usr/bin/env python
# encoding: utf-8

from meegloo.oembed.blackbird import embed_tweet_html

URL_PATTERNS = {
	'bliptv': (r'^https?://(.+\.)?blip\.tv/file/.+$',
		'http://blip.tv/oembed/?%s', 'json'
	),
	'clikthrough': (r'^https?://(www\.)?clikthrough\.com/theater/.+$', 
		'http://clikthrough.com/services/oembed/?%s', 'json'
	),
	'dailymotion': (r'^https?://(www\.)?dailymotion\.com/video/.+$',
		'http://www.dailymotion.com/api/oembed/?%s', 'json'
	),
	'dotsub': (r'^https?://(www\.)?dotsub\.com/view/.+$',
		'http://dotsub.com/services/oembed?%s', 'json'
	),
	'flickr': (r'^https?://(www\.)?flickr\.com/photos/.+$',
		'http://www.flickr.com/services/oembed/?%s', 'xml'
	),
	'hulu': (r'^https?://(www\.)?hulu\.com/watch/.+$',
		'http://www.hulu.com/api/oembed.json?%s', 'json'
	),
	'kinomap': (r'^https?://(www\.)?kinomap\.com/.+$',
		'http://www.kinomap.com/oembed?%s', 'xml'
	),
	'nfb': (r'^https?://(www\.)?nfb\.ca/film/.+$',
		'http://www.nfb.ca/remote/services/oembed/?%s',
		'xml'
	),
	'photobucket': (r'^https?://(.+\.)?photobucket\.com/(albums|groups)/.+$', 
		'http://photobucket.com/oembed?%s', 'json'
	),
	'qik': (r'^https?://(www\.)?qik\.com/video/.+$',
		'http://qik.com/api/oembed.json?%s', 'json'
	),
	'revision3': (r'^https?://(www\.)?revision3\.com/.+$',
		'http://revision3.com/api/oembed/?%s', 'json'
	),
	'scribd': (r'^https?://(www\.)?scribd\.com/doc/.+$',
		'http://www.scribd.com/services/oembed?%s', 'json'
	),
	'twitter': (r'^https?://twitter\.com/(#!/)?[\w]+/status(?:es)?/\d+', embed_tweet_html, 'html'),
	'viddler': (r'^https?://(www\.)?viddler\.com/explore/.+$',
		'http://lab.viddler.com/services/oembed/?%s', 'xml'
	),
	'vimeo': (r'^https?://(www\.)?vimeo\.com/.+$',
		'http://vimeo.com/api/oembed.json?%s', 'json'
	),
	'yfrog': (r'^https?://(www\.)?yfrog\.(com|ru|com\.tr|it|fr|co\.il|co\.uk|com\.pl|pl|eu|us)/.+$', 
		'http://www.yfrog.com/api/oembed?%s', 'json'
	),
	'youtube': (r'^https?://(www\.)?youtube\.com/watch\?v=.+$',
		'http://www.youtube.com/oembed?%s', 'json'
	),
}