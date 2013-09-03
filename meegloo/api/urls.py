#!/usr/bin/env python
# encoding: utf-8

from django.conf.urls.defaults import *
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from piston.authentication import OAuthAuthentication
from piston import authentication
from meegloo.api.handlers import *
from meegloo.api.resources import *

auth = OAuthAuthentication() # authentication.HttpBasicAuthentication()
auth_handler = CsrfExemptResource(UserHandler, authentication = auth)
user_search_handler = CsrfExemptResource(UserSearchHandler, authentication = auth)
follower_handler = CsrfExemptResource(FollowerHandler, authentication = auth)
following_handler = CsrfExemptResource(FollowingHandler, authentication = auth)
check_username_handler = CsrfExemptResource(CheckUsernameHandler)
oauth_tokens_handler = CsrfExemptResource(OAuthTokenHandler, authentication = auth)
category_handler = CsrfExemptResource(CategoryHandler, authentication = auth)
stream_handler = CsrfExemptResource(StreamHandler, authentication = auth)
network_handler = CsrfExemptResource(NetworkHandler, authentication = auth)
my_stream_handler = CsrfExemptResource(MyStreamHandler, authentication = auth)
following_stream_handler = CsrfExemptResource(FollowingStreamHandler, authentication = auth)
near_stream_handler = CsrfExemptResource(NearbyStreamHandler, authentication = auth)
trending_stream_handler = CsrfExemptResource(TrendingStreamHandler, authentication = auth)
post_handler = CsrfExemptResource(PostHandler, authentication = auth)
post_comments_handler = CsrfExemptResource(PostCommentHandler, authentication = auth)
post_answers_handler = CsrfExemptResource(PostAnswerHandler, authentication = auth)
my_post_handler = CsrfExemptResource(MyPostHandler, authentication = auth)

urlpatterns = patterns('',
	url(r'^user/$', auth_handler, name = 'api_user'),
	url(r'^user/search/$', user_search_handler, name = 'api_user_search'),
	url(r'^user/followers/$', follower_handler, name = 'api_followers'),
	url(r'^user/following/$', following_handler, name = 'api_following'),
	url(r'^user/following/(?P<followee>[\w]+)/$', following_handler, name = 'api_follow'),
	url(r'^user/(?P<username>\w+)/$', auth_handler, name = 'api_user'),
	url(r'^user/(?P<username>\w+)/followers/$', follower_handler, name = 'api_user_followers'),
	url(r'^user/(?P<username>\w+)/following/$', following_handler, name = 'api_user_following'),
	url(r'^user/(?P<username>\w+)\.png$', 'meegloo.api.views.user_avatar'),
	url(r'^user/(?P<username>\w+)/(?P<size>\d+)\.png$', 'meegloo.api.views.user_avatar'),
	url(r'^check-username/$', check_username_handler, name = 'api_user_check'),
	url(r'^auth/tokens/$', oauth_tokens_handler, name = 'api_tokens'),
	url(r'^networks/$', network_handler, name = 'api_networks'),
	url(r'^networks/(?P<id>\d+)/$', network_handler, name = 'api_network'),
	url(r'^networks/(?P<id>\d+)\.png$', 'meegloo.api.views.network_icon'),
	url(r'^categories/$', category_handler, name = 'api_categories'),
	url(r'^streams/$', stream_handler, name = 'api_streams'),
	url(r'^streams/near/$', near_stream_handler, name = 'api_streams_near'),
	url(r'^streams/trending/$', trending_stream_handler, name = 'api_streams_trending'),
	url(r'^streams/mine/$', my_stream_handler, name = 'api_streams_mine'),
	url(r'^streams/following/$', following_stream_handler, name = 'api_streams_following'),
	url(r'^streams/(?P<slug>[\w-]+)/$', stream_handler, name = 'api_streams'),
	url(r'^streams/(?P<stream>[\w-]+)/posts/$', post_handler, name = 'api_posts'),
	url(r'^streams/(?P<stream>[\w-]+)/posts/mine/$', my_post_handler, name = 'api_posts_mine'),
	url(r'^streams/(?P<stream>[\w-]+)/posts/(?P<id>\d+)/$', post_handler, name = 'api_posts'),
	url(r'^streams/(?P<stream>[\w-]+)/posts/(?P<id>\d+)/comments/$', post_comments_handler, name = 'api_post_comments'),
	url(r'^streams/(?P<stream>[\w-]+)/posts/(?P<id>\d+)/answer/$', post_answers_handler, name = 'api_post_answers'),
	url(r'^streams/(?P<stream>[\w-]+)/posts/(?P<id>\d+)\.png$',
		'meegloo.api.views.post_thumbnail'
	),
	url(r'^streams/(?P<stream>[\w-]+)/posts/(?P<id>\d+)/(?P<size>\d{2,3}x\d{2,3})\.png$',
		'meegloo.api.views.post_thumbnail'
	),
	url(r'^streams/(?P<stream>[\w-]+)/posts/(?P<id>\d+)\.html$',
		'meegloo.api.views.post'
	),
	url(r'^streams/(?P<stream>[\w-]+)/posts/(?P<id>\d+)/comments\.html$',
		'meegloo.api.views.comments'
	),
)

urlpatterns += patterns('meegloo.api.views',
	url(r'^oauth/authorise/mobile/$', 'oauth_user_auth'),
	url(r'^oauth/register/mobile/$', 'oauth_register'),
)

urlpatterns += patterns('',
	url(r'^oauth/request-token/$', csrf_exempt(authentication.oauth_request_token)),
	url(r'^oauth/authorise/$', csrf_exempt(authentication.oauth_user_auth)),
	url(r'^oauth/access-token/$', csrf_exempt(authentication.oauth_access_token)),
)