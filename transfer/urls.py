
from django.conf import settings
from django.conf.urls.defaults import *


urlpatterns = patterns('',
    # static server
    url(r'^media/(.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),

    # segmentation
    url(r'^segmentation/', include('segmentation.urls')),

    # base
    url(r'^', include('base.urls')),
)
