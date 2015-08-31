"""Template settings file. If using buildout, these settings will be the
base for bin/django. All settings can be overridden via a local_settings.py
file"""


INSTALLED_APPS = [
    'haystack',
    'regcore',
    'regcore_read',
    'regcore_write',
    'south'
]

SECRET_KEY = 'v^p)1cwc)%td*szt7lt-(nl=bf)k07t%65*t(mi1f!*18dz9m@'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'eregs.db'
    }
}

TEST_RUNNER = 'django_nose.runner.NoseTestSuiteRunner'

ROOT_URLCONF = 'regcore.urls'

DEBUG = True

BACKENDS = {
    'regulations': 'regcore.db.django_models.DMRegulations',
    'layers': 'regcore.db.django_models.DMLayers',
    'notices': 'regcore.db.django_models.DMNotices',
    'diffs': 'regcore.db.django_models.DMDiffs'
}

NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=regcore,regcore_read,regcore_write'
]

ELASTIC_SEARCH_URLS = []
ELASTIC_SEARCH_INDEX = 'eregs'

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://localhost:8983/solr'
    }
}

try:
    from local_settings import *
except ImportError:
    pass
