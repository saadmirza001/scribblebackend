from __future__ import absolute_import, unicode_literals

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
newApp = Celery("backend")

newApp.config_from_object('django.conf:settings', namespace="CELERY")

newApp.autodiscover_tasks()