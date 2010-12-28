# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

from admin import admin_site


urlpatterns = patterns('',
    # static server
    url(r'^media/(.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),

    # segmentation
    url(r'^segmentation/', include('segmentation.urls')),

    # methods
    url(r'^methods/', include('methods.urls')),

    # base
    url(r'^', include('base.urls')),

    # sorl.thumbnail
    url(r'^', include('sorl.thumbnail.urls')),

    # admin_media
    (r'^admin/', include(admin_site.urls)),
)
