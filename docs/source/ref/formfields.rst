===========
Form fields
===========

.. py:module:: dynamic_forms.formfields


.. py:function:: format_display_label(cls_name)


.. py:function:: load_class_from_string(cls_string)


:class:`DynamicFormFieldRegistry`
=================================

.. py:class:: DynamicFormFieldRegistry(object)

   .. py:method:: get(key)

   .. py:method:: get_as_choices()

      .. versionchanged:: 0.3
         Returns a generator instead of a list

      Returns a generator that yields all registered dynamic form fields as
      2-tuples in the form ``(key, display_label)``.


   .. py:method:: register(cls)

   .. py:method:: unregister(key)


.. py:data:: formfield_registry

   .. versionadded:: 0.3
      Use this instead of :data:`dynamic_form_field_registry`


.. py:data:: dynamic_form_field_registry

   .. deprecated:: 0.3
      Deprecated in favor of :data:`formfield_registry`

.. py:decorator:: dynamic_form_field(cls)

   A class decorator to register the class as a dynamic form field in the
   :class:`DynamicFormFieldRegistry`.


Base Form Field Classes
=======================

:class:`DFFMetaclass`
---------------------

.. py:class:: DFFMetaclass()

   Metaclass that inspects the ``Meta`` class of a class inheriting from
   :class:`BaseDynamicFormField` and merges the different attributes that are
   later being passed to the respective :class:`django.forms.Field`.

   You are free to add an attribute ``_exclude`` of type ``list`` or ``tuple``
   to the ``Meta`` class of a field to exclude any attributes inherited from a
   super DynamicFormField. Look at the implementation of the
   :class:`BooleanField` for an example.


:class:`BaseDynamicFormField`
-----------------------------

.. py:class:: BaseDynamicFormField()

   .. py:attribute:: cls

      ``None``

   .. py:attribute:: display_label

      ``None``

   .. py:attribute:: widget

      ``None``

   .. py:attribute:: options

   .. py:class:: Meta

      .. py:attribute:: help_text

         [six.string_types, '', (forms.CharField, forms.Textarea)]
      
      .. py:attribute:: required

         [bool, True, forms.NullBooleanField]

   .. py:method:: __init__(name, label, widget_attrs={}, **kwargs)

   .. py:method:: __str__()
                  __unicode__()

   .. py:method:: construct([**kwargs])

   .. py:method:: contribute_to_form(form)

   .. py:method:: get_display_label()

      Returns a class's :attr:`display_label` is defined or calls :func:`format_display_label` with the class's name.

      This function is only available to the class itself. It is not callable from an instance. 

   .. py:method:: get_widget_attrs()

   .. py:method:: set_options([**kwargs])

   .. py:method:: options_valid()

   .. py:classmethod:: do_display_data()

      Default: ``True``


Default Fields
==============

.. py:class:: BooleanField()

   .. py:attribute:: cls

      ``'django.forms.BooleanField``

   .. py:attribute:: display_label

      ``'Boolean``

   .. py:class:: Meta

      .. py:attribute:: _exclude

         ``('required',)``


.. py:class:: ChoiceField()

   .. py:attribute:: cls

      ``'django.forms.ChoiceField``

   .. py:attribute:: display_label

      ``'Choices``

   .. py:class:: Meta

      .. py:attribute:: choices

         [six.string_types, '', (forms.CharField, forms.Textarea)]

   .. py:method:: construct([**kwargs])

   .. py:method:: options_valid()


.. py:class:: DateField()

   .. py:attribute:: cls

      ``'django.forms.DateField``

   .. py:attribute:: display_label

      ``'Date``

   .. py:class:: Meta

      .. py:attribute:: localize

         [bool, True, forms.NullBooleanField]


.. py:class:: DateTimeField()

   .. py:attribute:: cls

      ``'django.forms.DateTimeField``

   .. py:attribute:: display_label

      'Date and Time'

   .. py:class:: Meta

      .. py:attribute:: localize

         [bool, True, forms.NullBooleanField]


.. py:class:: EmailField()

   .. py:attribute:: cls

      ``'django.forms.EmailField``

   .. py:attribute:: display_label

      ``'Email``


.. py:class:: IntegerField()

   .. py:attribute:: cls

      ``'django.forms.IntegerField``

   .. py:attribute:: display_label

      ``'Integer``

   .. py:class:: Meta

      .. py:attribute:: localize

         [bool, True, forms.NullBooleanField]
      
      .. py:attribute:: max_value

         [int, None, forms.IntegerField]

      .. py:attribute:: min_value

         [int, None, forms.IntegerField]


.. py:class:: MultiLineTextField()

   .. py:attribute:: cls

      ``'django.forms.CharField``

   .. py:attribute:: display_label

      ``'Multi Line Text``

   .. py:attribute:: widget

      ``'django.forms.widgets.Textarea``


.. py:class:: SingleLineTextField()

   .. py:attribute:: cls

      ``'django.forms.CharField``

   .. py:attribute:: display_label

      ``'Single Line Text``

   .. py:class:: Meta
      
      .. py:attribute:: max_length

         [int, None, forms.IntegerField]

      .. py:attribute:: min_length

         [int, None, forms.IntegerField]


.. py:class:: TimeField()

   .. py:attribute:: cls

      ``'django.forms.TimeField``

   .. py:attribute:: display_label

      ``'Time``

   .. py:class:: Meta

      .. py:attribute:: localize

         [bool, True, forms.NullBooleanField]
