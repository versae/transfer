# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from methods.forms import MethodForm, StepFormSet, SelectMethodForm
from methods.models import Method

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
    return render_to_response('apply.html',
                              {'image_object': image_object,
                               'select_method_form': select_method_form},
                              context_instance=RequestContext(request))


def methods_form(request, method_id):
    method_object = None
    if True:
        method_object = Method.objects.get(id=method_id)
        method_form = MethodForm(instance=method_object)
    return render_to_response('form.html',
                              {'method_form': method_form},
                              context_instance=RequestContext(request))
