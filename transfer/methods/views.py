# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
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
            image_object.final = step_formset.apply_method(image_object.image)
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
