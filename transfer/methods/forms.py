# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from django.utils.translation import gettext as _

from methods.models import Function, Method, Step


class FunctionForm(ModelForm):

    class Meta:
        model = Function


class MethodForm(ModelForm):

    class Meta:
        model = Method


class StepForm(ModelForm):

    class Meta:
        model = Step

StepFormSet = inlineformset_factory(Function, Step)


class SelectMethodForm(forms.Form):

    method = forms.ModelChoiceField(queryset=Method.objects.all())
