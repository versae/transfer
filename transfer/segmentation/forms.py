# -*- coding: utf-8 -*-
from django.forms import ModelForm

from segmentation.models import Image, STATUS_DICT


class InitialImageForm(ModelForm):

    class Meta:
        model = Image
        exclude = ("image_mask", "image_vertical_lines", "status", "small_ccs",
                   "medium_ccs", "large_ccs", "preprocessed_image",
                   "final_regions")


class PreprocessImageForm(InitialImageForm):

    def save(self, *args, **kwargs):
        self.instance.status = STATUS_DICT["PREPROCESSED"]
        super(PreprocessImageForm, self).save(*args, **kwargs)


class FiltersImageForm(InitialImageForm):

    def save(self, *args, **kwargs):
        self.instance.status = STATUS_DICT["FILTERED"]
        super(PreprocessImageForm, self).save(*args, **kwargs)


class TabStopsImageForm(InitialImageForm):

    def save(self, *args, **kwargs):
        self.instance.status = STATUS_DICT["TAB-STOPS"]
        super(PreprocessImageForm, self).save(*args, **kwargs)


class LayoutImageForm(InitialImageForm):

    def save(self, *args, **kwargs):
        self.instance.status = STATUS_DICT["COLUM-LAYOUT"]
        super(PreprocessImageForm, self).save(*args, **kwargs)
