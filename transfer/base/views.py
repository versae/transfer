# -*- coding: utf-8 -*-
from django.shortcuts import HttpResponse, render_to_response
from django.template import RequestContext

from base.forms import ImageForm


def index(request):
    image_form = ImageForm()
    return render_to_response('index.html',
                              {'image_form': image_form},
                              context_instance=RequestContext(request))
