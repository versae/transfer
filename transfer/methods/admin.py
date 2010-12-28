from django.contrib import admin
from methods.models import Function, Method, Step


class StepInline(admin.TabularInline):

    model = Method.functions.through
    extra = 1
#    raw_id_fields = ('method', 'function')


class StepAdmin(admin.ModelAdmin):

    pass


class FunctionAdmin(admin.ModelAdmin):

    inlines = (StepInline, )


class MethodAdmin(admin.ModelAdmin):

    inlines = (StepInline, )
    exclude = ("functions", )
