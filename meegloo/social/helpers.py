#!/usr/bin/env python
# encoding: utf-8

def format_tweet(text, tags, url):
	tags = [t for t in set(tags)]
	tags.sort()
	tags = ' '.join(tags)
	
	length = 135 - (tags and (len(tags) + 1) or 0) - len(url)
	reduced = False
	
	tweet = text
	while len(tweet) > length:
		space = tweet.rfind(' ')
		if space > -1:
			tweet = tweet[:space]
		else:
			tweet = tweet[:length]

		reduced = True
	
	tweet += (reduced and '... ' or ': ') + url
	if tags:
		tweet += ' ' + tags
	
	return tweet