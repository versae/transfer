# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext as _

WORKFLOW_STATUS = (
    ('I', u'Initial'),
    ('P', u'Preprocessed'),
    ('F', u'Filtered'),
    ('C', u'Cleaned tab-stops'),
    ('L', u'Found the column layout'),
    ('R', u'Final regions'),
)


class Image(models.Model):
    title = models.CharField(_(u'Title'), max_length=200)
    image = models.ImageField(_(u'Image'), upload_to='images')
    image_mask = models.ImageField(_(u'Image mask'), upload_to='images',
                                  blank=True, null=True)
    image_vertical_lines = models.ImageField(_(u'Image vertical lines'),
                                             upload_to='images',
                                             blank=True, null=True)
    status = models.CharField(_(u'Status'), max_length=1,
                              choices=WORKFLOW_STATUS)
    small_ccs = models.TextField(_(u'Small Connected Components'),
                                 blank=True, null=True)
    medium_ccs = models.TextField(_(u'Medium Connected Components'),
                                  blank=True, null=True)
    large_ccs = models.TextField(_(u'Large Connected Components'),
                                 blank=True, null=True)
    regions = models.TextField(_(u'Final regions'), blank=True, null=True)
    notes = models.TextField(_(u'Notes'), blank=True, null=True)

    def __unicode__(self):
        return u"%s (%s)" % (self.title, self.image.url)
