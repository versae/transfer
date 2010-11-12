# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('segmentation.views',
#    url(r'^$', 'index',
#        name="segmentation_index"),
    url(r'^initial/$', 'initial',
        name="segmentation_initial"),
    url(r'^preprocess/(?P<image_id>\d+)/$', 'preprocess',
        name="segmentation_preprocess"),
    url(r'^filters/(?P<image_id>\d+)/$', 'filters',
        name="segmentation_filters"),
    url(r'^tabstops/(?P<image_id>\d+)/$', 'tabstops',
        name="segmentation_tabstops"),
    url(r'^layout/(?P<image_id>\d+)/$', 'layout',
        name="segmentation_layout"),
    url(r'^final/(?P<image_id>\d+)/$', 'final',
        name="segmentation_final"),
)
