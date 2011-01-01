# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('methods.views',
    url(r'^apply/(?P<image_id>\d+)/$', 'methods_apply',
        name="methods_apply"),
    url(r'^form/(?P<method_id>\d+)/$', 'methods_form',
        name="methods_form"),
    url(r'^list/(?P<mode>\w+)/$', 'methods_list',
        name="methods_list"),
    url(r'^create/$', 'methods_editcreate',
        name="methods_create"),
    url(r'^edit/(?P<method_id>\d+)/$', 'methods_editcreate',
        name="methods_edit"),
)
