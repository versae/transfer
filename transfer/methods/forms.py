# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm
from django.forms.models import modelformset_factory
from django.utils.translation import gettext as _

from methods.models import Function, Method, Step


class FunctionForm(ModelForm):

    class Meta:
        model = Function


class MethodForm(ModelForm):

    class Meta:
        model = Method


class CustomStepForm(ModelForm):

    class Meta:
        model = Step

    def __init__(self, *args, **kwargs):
        super(CustomStepForm, self).__init__(*args, **kwargs)
        if self.instance:
            arguments = self.instance.function.arguments
            self.initial.update({'values': arguments})
            self.fields['values'].label = unicode(self.instance)

StepFormSet = modelformset_factory(Step,
                                   exclude=('order', 'inputs', 'method',
                                            'function'),
                                   extra=0,
                                   form=CustomStepForm)


class SelectMethodForm(forms.Form):

    class Media:
        js = (u"https://ajax.googleapis.com/ajax/libs/jquery/1.4.3/jquery.min.js",
              u"js/methods.apply.js")

    method = forms.ModelChoiceField(queryset=Method.objects.all())
