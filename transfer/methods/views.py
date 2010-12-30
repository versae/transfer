# -*- coding: utf-8 -*-
from cStringIO import StringIO
from PIL import Image as PILImage
from os import path

from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from methods.forms import MethodForm, StepFormSet, SelectMethodForm
from methods.models import Method, Step

from segmentation.models import Image


def methods_create(request):
    step_formset = StepFormSet()
    return render_to_response('create.html',
                              {'step_formset': step_formset},
                              context_instance=RequestContext(request))


def methods_list(request):
    return render_to_response('list.html',
                              {},
                              context_instance=RequestContext(request))


def methods_apply(request, image_id):
    image_object = Image.objects.get(id=image_id)
    select_method_form = SelectMethodForm()
    data = request.POST
    if data:
        step_formset = StepFormSet(data=data)
        if step_formset.is_valid():
            temp_handle = StringIO()
            preview = (data["id_preview_value"].lower() == "true")
            handwritten_mask = step_formset.exec_steps(image_object.image,
                                                       preview=preview)
            handwritten_mask.save(temp_handle, 'png')
            temp_handle.seek(0)
            suf = SimpleUploadedFile(path.split(image_object.image.name)[-1],
                                     temp_handle.read(),
                                     content_type='image/png')
            name = suf.name
            if "." in name:
                name = name.split(".")[0]
            image_object.handwritten_mask.save("%s_h.png" % name, suf)
            image_object.save()
    return render_to_response('apply.html',
                              {'image_object': image_object,
                               'select_method_form': select_method_form},
                              context_instance=RequestContext(request))


def methods_run(request, image_id, method_id, preview=None):
    image_object = Image.objects.get(id=image_id)
    method_object = Method.objects.get(id=method_id)
    select_method_form = SelectMethodForm()
    return render_to_response('apply.html',
                              {'image_object': image_object,
                               'select_method_form': select_method_form},
                              context_instance=RequestContext(request))


def methods_form(request, method_id):
    method_object = None
    if request.is_ajax():
        method_object = Method.objects.get(id=method_id)
        queryset = Step.objects.filter(method=method_object).order_by('order')
        step_formset = StepFormSet(queryset=queryset)
    return render_to_response('form.html',
                              {'step_formset': step_formset},
                              context_instance=RequestContext(request))
