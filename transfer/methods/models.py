# -*- coding: utf-8 -*-
from django.db import models
from django.utils.importlib import import_module
from django.utils.translation import gettext as _
from django.utils.simplejson import loads, dumps

TYPES_CHOICES = (
    ('I', u'Image'),
    ('B', u'Boolean'),
    ('N', u'Number'),
    ('S', u'String'),
    ('D', u'Dictionary'),
    ('L', u'List'),
)


class Function(models.Model):
    name = models.CharField(_(u'Name'), max_length=200)
    description = models.TextField(_(u'Description'), blank=True, null=True)
    arguments = models.TextField((u'Arguments'), blank=True, null=True)
    function = models.CharField(_(u'Function'), max_length=100)
    module = models.CharField(_(u'Module'), max_length=200)

    def __unicode__(self):
        return u"%s" % (self.name)

    def import_function(self):
        return getattr(import_module(self.module), self.function)


#class Argument(models.Model):
#    name = models.CharField(_(u'Name'), max_length=200)
#    type = models.CharField(_(u'Type'), max_length=1, choices=TYPES_CHOICES)
#    description = models.TextField(_(u'Description'), blank=True, null=True)
#    optional = models.BooleanField(_(u'Optional'))
#    value = models.CharField(_(u'Value'), max_length=250)
#    step = models.ForeignKey(Step, verbose_name=_(u'step'))

#    def __unicode__(self):
#        return u"%s" % (self.name)


class Method(models.Model):
    name = models.CharField(_(u'Name'), max_length=200)
    functions = models.ManyToManyField(Function, verbose_name=_(u'functions'),
                                       through='Step')

    def __unicode__(self):
        return u"%s" % (self.name)

    def apply_method(self, image):
        out = image
#        for step in self.steps.steps.order_by('order'):
#            out = step.exec_function(out)
        return out


class Step(models.Model):
    function = models.ForeignKey(Function, verbose_name=_(u'function'))
    method = models.ForeignKey(Method, verbose_name=_(u'method'))
    values = models.TextField((u'Values'), blank=True, null=True)
    order = models.PositiveIntegerField(_(u'Order'))
    input = models.PositiveIntegerField(_(u'Input'), blank=True, null=True,
                                        default=0)

    def __unicode__(self):
        if self.input == 0:
            input_var = u"INPUT_IMAGE"
        else:
            input_var = u"#%s" % (self.input)
        if self.values:
            input_var = u"%s, " % (input_var)
        return u"#%s ← %s(%s%s)" % (self.order, self.function.name, input_var,
                                    self.values)

    def exec_function(self, image):
        func = self.function.import_function()
        vals = self._get_vals_dict()
        return func(image, **vals)

    def _get_vals_dict(self):
        return loads(self.values)
