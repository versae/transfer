# -*- coding: utf-8 -*-
from django.forms import ModelForm

from base.models import Image


class ImageForm(ModelForm):

    class Meta:
        model = Image
        exclude = ("image_mask", "image_vertical_lines", "status", "small_ccs",
                   "medium_ccs", "large_ccs", "regions")
