# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext as _

STATUS_DICT = {
    'INITIAL': 'I',
    'PREPROCESSED': 'P',
    'FILTERED': 'F',
    'TAB-STOPS': 'T',
    'COLUM-LAYOUT': 'C',
    'FINAL-REGIONS': 'R',
}

WORKFLOW_STATUS = (
    ('I', u'Initial'),
    ('P', u'Preprocessed'),
    ('F', u'Filtered'),
    ('T', u'Tab-stops'),
    ('C', u'Column layout'),
    ('R', u'Final regions'),
)


class Image(models.Model):
    title = models.CharField(_(u'Title'), max_length=200)
    image = models.ImageField(_(u'Image'), upload_to='segmentation/images')
    final = models.ImageField(_(u'Image'), upload_to='segmentation/images')
    preprocessed_image = models.ImageField(_(u'Preprocessed image'),
                                           upload_to='segmentation/images',
                                           blank=True, null=True)
    image_mask = models.ImageField(_(u'Image mask'),
                                   upload_to='segmentation/images',
                                   blank=True, null=True)
    image_vertical_lines = models.ImageField(_(u'Image vertical lines'),
                                             upload_to='segmentation/images',
                                             blank=True, null=True)
    handwritten_mask = models.ImageField(_(u'Handwritting mask'),
                                        upload_to='segmentation/images',
                                        blank=True, null=True)
    status = models.CharField(_(u'Status'), max_length=1,
                              choices=WORKFLOW_STATUS, default='I')
    small_ccs = models.TextField(_(u'Small Connected Components'),
                                 blank=True, null=True)
    medium_ccs = models.TextField(_(u'Medium Connected Components'),
                                  blank=True, null=True)
    large_ccs = models.TextField(_(u'Large Connected Components'),
                                 blank=True, null=True)
    final_regions = models.TextField(_(u'Final regions'), blank=True,
                                     null=True)
    notes = models.TextField(_(u'Notes'), blank=True, null=True)

    def __unicode__(self):
        return u"%s (%s)" % (self.title, self.image.url)

    def get_initial(self):
        return self.objects.filter(status="I")

    def get_preprocessed(self):
        return self.objects.filter(status="P")

    def get_filtered(self):
        return self.objects.filter(status="F")

    def get_tab_stops(self):
        return self.objects.filter(status="T")

    def get_colum_layout(self):
        return self.objects.filter(status="C")

    def get_final(self):
        return self.objects.filter(status="R")
