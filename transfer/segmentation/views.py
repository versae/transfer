# -*- coding: utf-8 -*-
from PIL import Image as PILImage, ImageDraw as PILImageDraw

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from segmentation.forms import ImageForm
from segmentation.models import Image
from segmentation.utils import find_regions


def initial(request):
    if request.POST and request.FILES:
        image_form = ImageForm(request.POST, request.FILES)
        if image_form.is_valid():
            image_form.save()
            reverse_url = reverse("find_ccs")
            return HttpResponseRedirect(reverse_url)
    else:
        image_form = ImageForm()
    return render_to_response('initial.html',
                              {'image_form': image_form},
                              context_instance=RequestContext(request))


def preprocess(request, image_id):
    return render_to_response('initial.html',
                              {},
                              context_instance=RequestContext(request))

def filters(request, image_id):
    return render_to_response('initial.html',
                              {},
                              context_instance=RequestContext(request))

def tabstops(request, image_id):
    return render_to_response('initial.html',
                              {},
                              context_instance=RequestContext(request))

def layout(request, image_id):
    return render_to_response('initial.html',
                              {},
                              context_instance=RequestContext(request))

def final(request, image_id):
    return render_to_response('initial.html',
                              {},
                              context_instance=RequestContext(request))

def find_ccs(request, image_id):
    image_count = Image.objects.count()
    if not image_count:
        reverse_url = reverse("index")
        return HttpResponseRedirect(reverse_url)
    last_image = Image.objects.all()[image_count - 1]
    ccs = find_regions(PILImage.open(last_image.image.file.name))
#    draw = ImageDraw.Draw(im)
#    for r in regions:
#        draw.rectangle(r.box(), outline=(255, 0, 0))
#    del draw 
#    output = file("output.png", "wb")
#    im.save(output)
#    output.close()
    return render_to_response('ccs.html',
                              {'image': last_image,
                               'ccs': ccs},
                              context_instance=RequestContext(request))
