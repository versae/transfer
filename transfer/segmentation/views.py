# -*- coding: utf-8 -*-
from PIL import Image as PILImage

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.simplejson import dumps

from segmentation.forms import (PROCESSES_DICT, InitialImageForm,
                                PreprocessImageForm)
from segmentation.models import Image
from segmentation.utils import (find_regions, filter_regions,
                                get_otsu_threshold, region_serializer)


def initial(request):
    if request.POST and request.FILES:
        image_form = InitialImageForm(request.POST, request.FILES)
        if image_form.is_valid():
            image_object = image_form.save()
            process = request.POST.get("process", PROCESSES_DICT["ANCIENT"])
            if process == PROCESSES_DICT["HANDWRITTEN"]:
                reverse_url = reverse("segmentation_handwritten",
                                      args=[image_object.id])
            elif process == PROCESSES_DICT["CUSTOM"]:
                reverse_url = reverse("methods_apply",
                                      args=[image_object.id])
            else:
                reverse_url = reverse("segmentation_preprocess",
                                      args=[image_object.id])
            return HttpResponseRedirect(reverse_url)
    else:
        image_form = InitialImageForm()
    return render_to_response('initial.html',
                              {'image_form': image_form},
                              context_instance=RequestContext(request))


def preprocess(request, image_id):
    image_object = Image.objects.get(id=image_id)
    otsu_threshold = get_otsu_threshold(image_object.image.file)
    if request.POST:
        image_form = PreprocessImageForm(request.POST, instance=image_object)
        if image_form.is_valid():
            image_object = image_form.save()
            reverse_url = reverse("segmentation_filters",
                                  args=[image_object.id])
            return HttpResponseRedirect(reverse_url)
    else:
        image_form = PreprocessImageForm(instance=image_object,
                                         initial={"threshold": otsu_threshold})
    return render_to_response('preprocess.html',
                              {'image_object': image_object,
                               'image_form': image_form},
                              context_instance=RequestContext(request))


def filters(request, image_id):
    image_object = Image.objects.get(id=image_id)
    pil_image = PILImage.open(image_object.preprocessed_image.file.name)
    regions = find_regions(pil_image)
    # Based on paper http://research.google.com/pubs/pub35094.html
    factor = 5.4264e-5
    noise_heigth = factor * pil_image.size[1]
    filtered_regions = filter_regions(regions, noise_heigth)
    json_regions = dumps(filtered_regions, default=region_serializer)
    return render_to_response('filters.html',
                              {'image_object': image_object,
                               'regions': json_regions},
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


def handwritten(request, image_id):
    image_object = Image.objects.get(id=image_id)
    return render_to_response('handwritten.html',
                              {'image_object': image_object},
                              context_instance=RequestContext(request))
