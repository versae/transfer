# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('base.views',
    url(r'^$', 'index', name="index"),
)
