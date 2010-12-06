# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    # static server
    url(r'^media/(.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),

    # segmentation
    url(r'^segmentation/', include('segmentation.urls')),

    # base
    url(r'^', include('base.urls')),

    # admin_media
    (r'^admin/', include(admin.site.urls)),
)
