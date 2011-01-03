# -*- coding: utf-8 -*-
from cStringIO import StringIO
from os import path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import gettext as _

from methods.forms import (CustomStepFormSet, MethodForm, StepFormSet,
                           SelectMethodForm)
from methods.models import Method, Step, Function

from segmentation.models import Image


def methods_editcreate(request, method_id=None):
    method_object = None
    if method_id:
        method_object = Method.objects.get(id=method_id)
        step_formset = StepFormSet(instance=method_object)
        method_form = MethodForm(instance=method_object)
        mode = _(u"Edit")
    else:
        step_formset = StepFormSet(instance=Step())
        method_form = MethodForm()
        mode = _(u"Create")
    if request.POST:
        data = request.POST
        step_formset = StepFormSet(instance=method_object, data=data)
        method_form = MethodForm(instance=method_object, data=data)
        if step_formset.is_valid() and method_form.is_valid():
            method_object = method_form.save()
            step_formset = StepFormSet(instance=method_object, data=data)
            step_formset.save()
    return render_to_response('editcreate.html',
                              {'step_formset': step_formset,
                               'method_form': method_form,
                               'mode': mode},
                              context_instance=RequestContext(request))


def methods_list(request, mode):
    objects = None
    if mode == "functions":
        objects = Function.objects.all().order_by("name")
    elif mode == "methods":
        objects = Method.objects.all().order_by("name")
    return render_to_response('list.html',
                              {'mode': mode,
                               'objects': objects},
                              context_instance=RequestContext(request))


def methods_apply(request, image_id):
    image_object = Image.objects.get(id=image_id)
    select_method_form = SelectMethodForm()
    exec_errors = None
    if request.POST:
        data = request.POST
        step_formset = CustomStepFormSet(data=data)
        select_method_form = SelectMethodForm(data=data)
        if step_formset.is_valid():
            temp_handle = StringIO()
            preview = (data["id_preview_value"].lower() == "true")
            errors = []
            executed_steps = step_formset.exec_steps(image_object.image,
                                                     preview=preview,
                                                     errors=True)
            (handwritten_mask, exec_errors) = executed_steps
            handwritten_mask.save(temp_handle, 'png')
            temp_handle.seek(0)
            path_split = path.split(image_object.image.name)[-1]
            suf = SimpleUploadedFile(path_split,
                                     temp_handle.read(),
                                     content_type='image/png')
            name = suf.name
            if "." in name:
                name = name.split(".")[0]
            image_object.handwritten_mask.save("%s_h.png" % name, suf)
            image_object.save()
    return render_to_response('apply.html',
                              {'image_object': image_object,
                               'select_method_form': select_method_form,
                               'errors': exec_errors},
                              context_instance=RequestContext(request))


def methods_run(request, image_id, method_id, preview=None):
    image_object = Image.objects.get(id=image_id)
    # method_object = Method.objects.get(id=method_id)
    select_method_form = SelectMethodForm(data=request.POST)
    return render_to_response('apply.html',
                              {'image_object': image_object,
                               'select_method_form': select_method_form},
                              context_instance=RequestContext(request))


def methods_form(request, method_id):
    # method_object = None
    method_object = Method.objects.get(id=method_id)
    queryset = Step.objects.filter(method=method_object).order_by('order')
    step_formset = CustomStepFormSet(queryset=queryset)
    return render_to_response('form.html',
                              {'step_formset': step_formset},
                              context_instance=RequestContext(request))
