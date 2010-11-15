# -*- coding: utf-8 -*-
import base64

from cStringIO import StringIO
from PIL import Image as PILImage
from os import path

from django import forms
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import ModelForm
from django.utils.translation import gettext as _

from segmentation.models import Image, STATUS_DICT


class InitialImageForm(ModelForm):

    class Meta:
        model = Image
        exclude = ("image_mask", "image_vertical_lines", "status", "small_ccs",
                   "medium_ccs", "large_ccs", "preprocessed_image",
                   "final_regions")

    def save(self, *args, **kwargs):
        image = PILImage.open(self.instance.image.file)
        temp_handle = StringIO()
        greyscale_image = image.convert("L")
        greyscale_image.save(temp_handle, 'png')
        temp_handle.seek(0)
        suf = SimpleUploadedFile(path.split(self.instance.image.name)[-1],
                                 temp_handle.read(), content_type='image/png')
        name = suf.name
        if "." in name:
            name = name.split(".")[0]
        self.instance.preprocessed_image.save("%s_L.png" % suf.name, suf,
                                              save=False)
        return super(InitialImageForm, self).save(*args, **kwargs)


class PreprocessImageForm(ModelForm):

    class Meta:
        model = Image
        exclude = ("image_mask", "image_vertical_lines", "status", "small_ccs",
                   "medium_ccs", "large_ccs", "preprocessed_image",
                   "final_regions", "image", "notes", "title")

    threshold = forms.IntegerField(_(u"Binarization threshold"))
    base64_image = forms.CharField(_(u"Base64 encoded image"),
                                   widget=forms.HiddenInput)

    def clean_base64_image(self):
        base64_string = self.cleaned_data["base64_image"]
        decoded_string = base64.b64decode(base64_string.split(",")[1])
        temp_handle = StringIO()
        temp_handle.write(decoded_string)
        temp_handle.seek(0)
        suf = SimpleUploadedFile(path.split(self.instance.image.name)[-1],
                                 temp_handle.read(), content_type='image/png')
        return suf

    def save(self, *args, **kwargs):
        suf = self.cleaned_data['base64_image']
        self.instance.preprocessed_image.save(suf.name, suf,
                                              save=False)
        self.instance.status = STATUS_DICT["PREPROCESSED"]
        return super(PreprocessImageForm, self).save(*args, **kwargs)


class FiltersImageForm(InitialImageForm):

    def save(self, *args, **kwargs):
        self.instance.status = STATUS_DICT["FILTERED"]
        return super(PreprocessImageForm, self).save(*args, **kwargs)


class TabStopsImageForm(InitialImageForm):

    def save(self, *args, **kwargs):
        self.instance.status = STATUS_DICT["TAB-STOPS"]
        return super(PreprocessImageForm, self).save(*args, **kwargs)


class LayoutImageForm(InitialImageForm):

    def save(self, *args, **kwargs):
        self.instance.status = STATUS_DICT["COLUM-LAYOUT"]
        return super(PreprocessImageForm, self).save(*args, **kwargs)
