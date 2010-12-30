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
    inputs = models.PositiveIntegerField(_(u'# Image inputs'), default=1)
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
    description = models.TextField(_(u'Description'), blank=True, null=True)

    def __unicode__(self):
        return u"%s" % (self.name)


class Step(models.Model):
    order = models.PositiveIntegerField(_(u'Order'))
    inputs = models.CommaSeparatedIntegerField(_(u'Inputs'), blank=True,
                                               null=True, max_length=10,
                                               default="0")
    function = models.ForeignKey(Function, verbose_name=_(u'function'))
    method = models.ForeignKey(Method, verbose_name=_(u'method'))
    values = models.TextField((u'Values'), blank=True, null=True)

    def __unicode__(self):
        inputs = self.prepare_inputs()
        inputs_vars = []
        for input in inputs:
            if not input or input >= self.order:
                inputs_vars.append(u"INPUT")
            else:
                inputs_vars.append(u"#%s" % (input))
        inputs_str = ", ".join(inputs_vars)
        if self.values:
            inputs_str = u"%s, " % (inputs_str)
        return u"#%s ← %s(%s%s)" % (self.order, self.function.name, inputs_str,
                                    self.values)

    def prepare_inputs(self):
        return map(lambda x: int(x.strip()), self.inputs.split(","))

    def exec_function(self, inputs, values=None):
        func = self.function.import_function()
        vals = self._get_vals_dict(values)
        return func(*inputs, **vals)

    def _get_vals_dict(self, values=None):
        return eval("(lambda **kw: kw)(%s)" % (values or self.values))
