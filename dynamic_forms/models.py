# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from collections import OrderedDict

from django.core.urlresolvers import reverse
from django.db import models
from django.db.transaction import atomic
from django.template.defaultfilters import slugify
from django.utils.crypto import get_random_string
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.html import format_html, format_html_join
from django.utils.translation import ugettext_lazy as _

from dynamic_forms.actions import action_registry
from dynamic_forms.conf import settings
from dynamic_forms.fields import TextMultiSelectField
from dynamic_forms.formfields import formfield_registry


@python_2_unicode_compatible
class FormModel(models.Model):
    name = models.CharField(_('Name'), max_length=50, unique=True)
    actions = TextMultiSelectField(_('Actions'), default='',
        choices=action_registry.get_as_choices())
    form_template = models.CharField(_('Form template path'), max_length=100,
        default='dynamic_forms/form.html',
        choices=settings.DYNAMIC_FORMS_FORM_TEMPLATES)
    allow_display = models.BooleanField(_('Allow display'), default=False,
        help_text=_('Allow a user to view the input at a later time. This '
            'requires the “Store in database” action to be active. The sender '
            'will be given a unique URL to recall the data.'))
    recipient_email = models.EmailField(_('Recipient email'), blank=True,
        null=True, help_text=_('Email address to send form data.'))
    display = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('Dynamic form')
        verbose_name_plural = _('Dynamic forms')

    def __str__(self):
        return self.name

    def get_fields_as_dict(self):
        """
        Returns an ``OrderedDict`` (``SortedDict`` when ``OrderedDict is not
        available) with all fields associated with this form where their name
        is the key and their label is the value.
        """
        return OrderedDict(self.fields.values_list('name', 'label').all())


@python_2_unicode_compatible
class FormFieldModel(models.Model):

    parent_form = models.ForeignKey(FormModel, on_delete=models.CASCADE,
        related_name='fields')
    field_type = models.CharField(_('Type'), max_length=255,
        choices=formfield_registry.get_as_choices())
    label = models.CharField(_('Label'), max_length=255)
    name = models.SlugField(_('Name'), max_length=50, blank=True)
    _options = models.TextField(_('Options'), blank=True, null=True)
    position = models.SmallIntegerField(_('Position'), blank=True, default=0)

    class Meta:
        ordering = ['parent_form', 'position']
        unique_together = ("parent_form", "name",)
        verbose_name = _('Form field')
        verbose_name_plural = _('Form fields')

    def __str__(self):
        return _('Field “%(field_name)s” in form “%(form_name)s”') % {
            'field_name': self.label,
            'form_name': self.parent_form.name,
        }

    def generate_form_field(self, form):
        field_type_cls = formfield_registry.get(self.field_type)
        field = field_type_cls(**self.get_form_field_kwargs())
        field.contribute_to_form(form)
        return field

    def get_form_field_kwargs(self):
        kwargs = self.options
        kwargs.update({
            'name': self.name,
            'label': self.label,
        })
        return kwargs

    @property
    def options(self):
        """Options passed to the form field during construction."""
        if not hasattr(self, '_options_cached'):
            self._options_cached = {}
            if self._options:
                try:
                    self._options_cached = json.loads(self._options)
                except ValueError:
                    pass
        return self._options_cached

    @options.setter
    def options(self, opts):
        if hasattr(self, '_options_cached'):
            del self._options_cached
        self._options = json.dumps(opts)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = slugify(self.label)

        given_options = self.options
        field_type_cls = formfield_registry.get(self.field_type)
        invalid = set(self.options.keys()) - set(field_type_cls._meta.keys())
        if invalid:
            for key in invalid:
                del given_options[key]
            self.options = given_options

        super(FormFieldModel, self).save(*args, **kwargs)


@python_2_unicode_compatible
class FormModelData(models.Model):
    form = models.ForeignKey(FormModel, on_delete=models.SET_NULL,
        related_name='data', null=True)
    value = models.TextField(_('Form data'), blank=True, default='')
    submitted = models.DateTimeField(_('Submitted on'), auto_now_add=True)
    display_key = models.CharField(_('Display key'), max_length=24, null=True,
        blank=True, db_index=True, default=None, unique=True,
        help_text=_('A unique identifier that is used to allow users to view '
                    'their sent data. Unique over all stored data sets.'))

    class Meta:
        verbose_name = _('Form data')
        verbose_name_plural = _('Form data')

    def __str__(self):
        return _('Form: “%(form)s” on %(date)s') % {
            'form': self.form,
            'date': self.submitted,
        }

    def save(self, *args, **kwargs):
        with atomic():
            if self.form.allow_display and not self.display_key:
                dk = get_random_string(24)
                while FormModelData.objects.filter(display_key=dk).exists():
                    dk = get_random_string(24)
                self.display_key = dk
            super(FormModelData, self).save(*args, **kwargs)

    @property
    def json_value(self):
            return OrderedDict(sorted(json.loads(self.value).items()))

    def pretty_value(self):
        try:
            value = format_html_join('',
                '<dt>{0}</dt><dd>{1}</dd>',
                (
                    (force_text(k), force_text(v))
                    for k, v in self.json_value.items()
                )
            )
            return format_html('<dl>{0}</dl>', value)
        except ValueError:
            return self.value
    pretty_value.allow_tags = True

    @property
    def show_url(self):
        """
        If the form this data set belongs to has
        :attr:`~FormModel.allow_display` ``== True``, return the permanent URL.
        If displaying is not allowed, return an empty string.
        """
        if self.form.allow_display:
            return reverse('dynamic_forms:data-set-detail',
                kwargs={'display_key': self.display_key})
        return ''

    @property
    def show_url_link(self):
        """
        Similar to :attr:`show_url` but wraps the display key in an `<a>`-tag
        linking to the permanent URL.
        """
        if self.form.allow_display:
            return format_html('<a href="{0}">{1}</a>', self.show_url, self.display_key)
        return ''
