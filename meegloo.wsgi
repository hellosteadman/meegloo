import os, sys
import django.core.handlers.wsgi

sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = sys.stderr

os.environ['DJANGO_SETTINGS_MODULE'] = 'meegloo.settings'
os.environ['PYTHON_EGG_CACHE'] = os.path.dirname(__file__) + '/.python-eggs'
os.environ['CELERY_LOADER'] = 'django'
application = django.core.handlers.wsgi.WSGIHandler()