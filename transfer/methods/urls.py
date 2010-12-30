# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('methods.views',
    url(r'^apply/(?P<image_id>\d+)/$', 'methods_apply',
        name="methods_apply"),
    url(r'^form/(?P<method_id>\d+)/$', 'methods_form',
        name="methods_form"),
    url(r'^list/(?P<element>\w+)/$', 'methods_list',
        name="methods_list"),
    url(r'^create/$', 'methods_create',
        name="methods_create"),
)
