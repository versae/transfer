# -*- coding: utf-8 -*-
from PIL import Image as PILImage

from django import forms
from django.forms import ModelForm
from django.forms.models import (BaseModelFormSet, modelformset_factory,
                                 inlineformset_factory)
from django.utils.translation import gettext as _

from methods.models import Function, Method, Step

from segmentation.utils import thumbnail


class FunctionForm(ModelForm):

    class Meta:
        model = Function


class MethodForm(ModelForm):

    class Meta:
        model = Method
        exclude = ('functions', )


class StepBaseFormSet(BaseModelFormSet):

    def __init__(self, *args, **kwargs):
        super(StepBaseFormSet, self).__init__(*args, **kwargs)

    def exec_steps(self, image_field, preview=False, errors=False):
        error_list = []
        if preview:
            image = thumbnail(PILImage.open(image_field.file))
        else:
            image = PILImage.open(image_field.file)

        def _get_variable(x):
            return variables.get(x, image)

        variables = {}
        for form in self.forms:
            try:
                step = form.instance
                inputs = map(_get_variable, step.prepare_inputs())
                variables[step.order] = step.exec_function(inputs,
                                                           values=step.values)
            except Exception as error:
                error_list.append((step, type(error), error.args))
        if step:
            output = _get_variable(step.order)
        else:
            output = image
        if errors:
            return output, error_list
        else:
            return output


class CustomStepForm(ModelForm):

    class Meta:
        model = Step

    def __init__(self, *args, **kwargs):
        super(CustomStepForm, self).__init__(*args, **kwargs)
        if self.instance:
            arguments = self.instance.function.arguments
            self.initial.update({'values': self.instance.values or arguments})
            self.fields['values'].label = unicode(self.instance)


CustomStepFormSet = modelformset_factory(Step,
                                       form=CustomStepForm,
                                       formset=StepBaseFormSet,
                                       exclude=('order', 'inputs', 'method',
                                                'function'),
                                       extra=0)


StepFormSet = inlineformset_factory(Method, Step,
                                    can_delete=True,
                                    extra=1)


class SelectMethodForm(forms.Form):

    class Media:
        js = (u"https://ajax.googleapis.com/ajax/libs/jquery/1.4.3/jquery.min.js",
              u"js/methods.apply.js")

    method = forms.ModelChoiceField(queryset=Method.objects.all())
