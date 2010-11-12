# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('base.views',
    url(r'^$', 'index', name="index"),
    url(r'^initial/(?P<image_id>\d+)?$', 'initial', name="initial"),
    url(r'^preprocess/(?P<image_id>\d+)?$', 'preprocess', name="preprocess"),
    url(r'^filter/(?P<image_id>\d+)?$', 'filter', name="filter"),
    url(r'^tabstops/(?P<image_id>\d+)?$', 'tabstops', name="tabstops"),
    url(r'^layout/(?P<image_id>\d+)?$', 'layout', name="layout"),
    url(r'^final/(?P<image_id>\d+)?$', 'final', name="final"),
)
