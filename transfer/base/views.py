# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext

from segmentation.models import Image


def index(request):
    images = Image.objects.all()
    return render_to_response('index.html',
                              {'images': images,
                               'is_home': True},
                              context_instance=RequestContext(request))
