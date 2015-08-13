# -*- coding: utf-8 -*-

from django.conf.urls import url

from .views import data_set_detail, form_handler, get_form, DynamicFormView

urlpatterns = [
    url(r'show/(?P<display_key>[a-zA-Z0-9]{24})/$', data_set_detail,
        name='data-set-detail'),
    url(r'^forms/$', DynamicFormView.as_view(), name='dynamic_form_handler'),
    url(r'^forms/(?P<form_id>[0-9]+)/$', DynamicFormView.as_view(), name='get_form')

]
