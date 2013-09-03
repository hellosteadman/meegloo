#!/usr/bin/env python
# encoding: utf-8

from os import path
from settings_local import *

TEMPLATE_DEBUG = True
THUMBNAIL_DEBUG = DEBUG
THUMBNAIL_FORMAT = 'PNG'

MANAGERS = ADMINS
TIME_ZONE = None
LANGUAGE_CODE = 'en'
COUNTRY_ID = 272
USE_I18N = True
USE_L10N = True
SITE_ROOT = path.abspath(path.dirname(__file__) + '/../')
MEDIA_ROOT = path.join(SITE_ROOT, 'media') + '/'
MEDIA_URL = '/media/'
STATIC_ROOT = path.join(SITE_ROOT, 'static') + '/'
STATIC_URL = '/static/'

SECRET_KEY = ')l6q0!_@%oo!s6vrmpmmh2eer7*y@0e)d7%dz16sf8z2)x5tby'

STATICFILES_DIRS = (
	# Put strings here, like '/home/html/static' or 'C:/www/django/static'.
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
)

STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader'
)

MIDDLEWARE_CLASSES = (
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.transaction.TransactionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'meegloo.api.middleware.ContentTypeMiddleware',
	'meegloo.urlshortening.middleware.URLShorteningMiddleware',
	'meegloo.networks.middleware.NetworkMiddleware',
	'meegloo.core.middleware.AdminMiddleware'
)

TEMPLATE_CONTEXT_PROCESSORS = (
	'django.core.context_processors.debug',
	'django.core.context_processors.i18n',
	'django.core.context_processors.request',
	'django.core.context_processors.media',
	'django.core.context_processors.csrf',
	'django.contrib.auth.context_processors.auth',
	'django.contrib.messages.context_processors.messages',
	'meegloo.core.context_processors.current_site',
	'meegloo.uploadify.context_processors.settings',
	'meegloo.registration.context_processors.forms',
	'meegloo.streams.context_processors.latest',
	'meegloo.streams.context_processors.settings',
	'meegloo.networks.context_processors.networks',
	'meegloo.viral.context_processors.competitions'
)

ROOT_URLCONF = 'meegloo.urls'

TEMPLATE_DIRS = (
	(path.join(SITE_ROOT, 'templates')),
)

INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.admin',
	'django.contrib.humanize',
	'django.contrib.markup',
	'django.contrib.staticfiles',
	'taggit',
	'sorl.thumbnail',
	'south',
	'raven.contrib.django',
	'piston',
	'haystack',
	'meegloo.api',
	'meegloo.registration',
	'meegloo.streams',
	'meegloo.networks',
	'meegloo.uploadify',
	'meegloo.social',
	'meegloo.oembed',
	'meegloo.urlshortening',
	'meegloo.analytics',
	'meegloo.core',
	'meegloo.mail',
	'meegloo.viral'
)

DEFAULT_FROM_EMAIL = 'hello@meegloo.com'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

INVALID_USERNAMES = (
	'', 'admin', 'blog', 'followers', 'following', 'mail', 'phpmyadmin', 'search', 'smtp', 'www'
)

INVALID_SLUGS = (
	'', 'about', 'admin', 'api', 'badges', 'categories', 'confirm-email', 'create', 'downloads', 'join',
	'login', 'logout', 'media', 'networks', 'oauth', 'privacy', 'profile', 'search', 'signup', 'streams',
	'tags', 'terms', 'win'
)

API_KEYS = {
	'flickr': '9c7f7691c6af611084c6af4e9e2fd059',
	'twitter': 'ClQgSvsM83SNCoZSHDlWQ',
	'google': 'ABQIAAAAZqA92uGy1jp1_GufUAqG4BSofQ9w8U_bbyFx2KTZ-zn7Ex-qLBRrvtLgoF2MA5VJwT7rg3q3sXfGDw'
}

OAUTH_CREDENTIALS = {
	'TWITTER': {
		'CONSUMER_KEY': 'JuPHx3I2dj1RhOu6SbrRag',
		'CONSUMER_SECRET': '8Du70f1zvn67me9WdxZeH31GJKa7nwMHFn8VEkPS8MQ',
		'SSL': True,
		'URLS': {
			'REQUEST_TOKEN': 'https://twitter.com/oauth/request_token',
			'ACCESS_TOKEN': 'https://twitter.com/oauth/access_token',
			'AUTHORISATION': 'https://twitter.com/oauth/authorize'
		},
		'BOT_TOKEN': '434256943-OYdjqTMJ7BvLM5fGhqYxeMal5d14warmVCa73yqF',
		'BOT_SECRET': 'fmZyhZBkx49ziMxrVc26lyOcqDBd9yFkgyE2KAk',
		'VERBOSE_NAME': 'Twitter',
		'FRIENDSHIPS': True
	},
	'FLICKR': {
		'CONSUMER_KEY': '9c7f7691c6af611084c6af4e9e2fd059',
		'CONSUMER_SECRET': '0041ecff2688bd92',
		'SERVER': 'www.flickr.com',
		'URLS': {
			'REQUEST_TOKEN': 'http://www.flickr.com/services/oauth/request_token',
			'ACCESS_TOKEN': 'http://www.flickr.com/services/oauth/access_token',
			'AUTHORISATION': (
				'http://www.flickr.com/services/oauth/authorize',
				{
					'perms': 'write'
				}
			)
		},
		'VERBOSE_NAME': 'Flickr',
		'FRIENDSHIPS': False
	},
	'FACEBOOK': {
		'CONSUMER_KEY': '193403867386972',
		'CONSUMER_SECRET': 'e75acc45c13a04e97016a879df116717',
		'URLS': {
			'DIALOG': 'https://www.facebook.com/dialog/oauth?client_id=193403867386972&redirect_uri=http%3A%2F%2Fmeegloo.com%2Foauth%2Ffacebook%2Freturn%2F&scope=publish_stream',
			'ACCESS_TOKEN': 'https://graph.facebook.com/oauth/access_token?client_id=193403867386972&redirect_uri=http%%3A%%2F%%2Fmeegloo.com%%2Foauth%%2Ffacebook%%2Freturn%%2F&client_secret=e75acc45c13a04e97016a879df116717&code=%s'
		},
		'VERBOSE_NAME': 'Facebook',
		'FRIENDSHIPS': True
	}
}

AUTH_PROFILE_MODULE = 'core.profile'
MAILCHIMP_API_KEY = '152980702cd408180a2e4cb31afad9e3-us2'
MAILCHIMP_LIST_ID = 'd4da5cc89b'

UPLOADIFY_PATH = '/media/uploadify/'
UPLOADIFY_UPLOAD_PATH = '%suploads' % MEDIA_URL

MAX_CONCURRENT_CONVERSIONS = 1
TEMP_DIR = path.join(SITE_ROOT, 'tmp')

UPLOADIFY_URL = '/media/js/uploadify/'

MIME_TYPE_ROUTES = (
	('photo', ('image/bmp', 'image/jpeg', 'image.gif', 'image/png', 'image/tiff')),
	('audio', ('audio/mp4a-latm', 'audio/mpeg', 'audio/ogg', 'audio/x-aac', 'audio/x-wav')),
	('video', ('video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-flv'))
)

FILE_EXTENSIONS = (
	'.aac', '.avi', '.bmp', '.flv', '.jpe', '.jpeg', '.jpg', '.m4a',
	'.mov', '.mp3', '.mp4', '.oga', '.png', '.tif', '.tiff', '.wav'
)

DOMAIN_SUFFIXES = (
	'.ac', '.ad', '.ae', '.af', '.ag', '.ai', '.al', '.am', '.an', '.ao', '.aq', '.ar',
	'.as', '.at', '.au', '.aw', '.az', '.ba', '.bb', '.bd', '.be', '.bf', '.bg', '.bh',
	'.bi', '.bj', '.bm', '.bn', '.bo', '.br', '.bs', '.bt', '.bv', '.bw', '.by', '.bz',
	'.ca', '.cc', '.cd', '.cf', '.cg', '.ch', '.ci', '.ck', '.cl', '.cm', '.cn', '.co',
	'.com', '.cr', '.cs', '.cu', '.cv', '.cx', '.cy', '.cz', '.de', '.dj', '.dk', '.dm',
	'.do', '.dz', '.ec', '.edu', '.ee', '.eg', '.eh', '.er', '.es', '.et', '.fi', '.fj',
	'.fk', '.fm', '.fo', '.fr', '.ga', '.gd', '.ge', '.gf', '.gg', '.gh', '.gi', '.gl',
	'.gm', '.gn', '.gov', '.gp', '.gq', '.gr', '.gs', '.gt', '.gu', '.gw', '.gy', '.hk',
	'.hm', '.hn', '.hr', '.ht', '.hu', '.id', '.ie', '.il', '.im', '.in', '.int', '.io',
	'.iq', '.ir', '.is', '.it', '.je', '.jm', '.jo', '.jp', '.ke', '.kg', '.kh', '.ki',
	'.km', '.kn', '.kp', '.kr', '.kw', '.ky', '.kz', '.la', '.lb', '.lc', '.li', '.lk',
	'.lr', '.ls', '.lt', '.lu', '.lv', '.ly', '.ma', '.mc', '.md', '.me', '.mg', '.mh',
	'.mil', '.mk', '.ml', '.mm', '.mn', '.mo', '.mp', '.mq', '.mr', '.ms', '.mt', '.mu',
	'.mv', '.mw', '.mx', '.my', '.mz', '.na', '.nc', '.ne', '.net', '.nf', '.ng', '.ni',
	'.nl', '.no', '.np', '.nr', '.nt', '.nu', '.nz', '.om', '.org', '.pa', '.pe', '.pf',
	'.pg', '.ph', '.pk', '.pl', '.pm', '.pn', '.pr', '.ps', '.pt', '.pw', '.py', '.qa',
	'.re', '.ro', '.ru', '.rw', '.sa', '.sb', '.sc', '.sd', '.se', '.sg', '.sh', '.si',
	'.sj', '.sk', '.sl', '.sm', '.sn', '.so', '.sr', '.st', '.sv', '.sy', '.sz', '.tc',
	'.td', '.tf', '.tg', '.th', '.tj', '.tk', '.tm', '.tn', '.to', '.tp', '.tr', '.tt',
	'.tv', '.tw', '.tz', '.ua', '.ug', '.uk', '.um', '.us', '.uy', '.uz', '.va', '.vc',
	'.ve', '.vg', '.vi', '.vn', '.vu', '.wf', '.ws', '.ye', '.yt', '.yu', '.za', '.zm', '.zw'
)

URL_SHORTENING_DOMAIN = 'glu.li'

HAYSTACK_SEARCH_ENGINE = 'xapian'
HAYSTACK_SITECONF = 'meegloo.search'
HAYSTACK_XAPIAN_PATH = path.abspath(path.dirname(__file__) + '/../search/')
HAYSTACK_INCLUDE_SPELLING = True

SESSION_COOKIE_DOMAIN = '.meegloo.com'

LOGGING = {
	'version': 1,
	'disable_existing_loggers': True,
	'root': {
		'level': 'WARNING',
		'handlers': ['sentry'],
	},
	'formatters': {
		'verbose': {
			'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
		},
	},
	'handlers': {
		'sentry': {
			'level': 'ERROR',
			'class': 'raven.contrib.django.handlers.SentryHandler',
		},
		'console': {
			'level': 'DEBUG',
			'class': 'logging.StreamHandler',
			'formatter': 'verbose'
		}
	},
	'loggers': {
		'django.db.backends': {
			'level': 'ERROR',
			'handlers': ['console'],
			'propagate': False
		},
		'raven': {
			'level': 'DEBUG',
			'handlers': ['console'],
			'propagate': False
		},
		'sentry.errors': {
			'level': 'DEBUG',
			'handlers': ['console'],
			'propagate': False
		}
	}
}