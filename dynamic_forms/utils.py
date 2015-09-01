import csv
import inspect
import json
import types

from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.utils.text import slugify


def is_old_style_action(func):
    if isinstance(func, types.FunctionType):
        # it's a regular function
        argspec = inspect.getargspec(func)
        return len(argspec.args) == 2
    else:
        # it's class with __call__()
        argspec = inspect.getargspec(func.__call__)
        return len(argspec.args) == 3  # mind the 'self' arg


def export_as_csv_action(description="Export selected form's data as a CSV file",
                         fields=None, exclude=None, header=True):
    """
    Snippet came from https://djangosnippets.org/snippets/2369/

    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row

    Snippet found at https://djangosnippets.org/snippets/2369/
    """
    def export_as_csv(modeladmin, request, queryset):
        """
        Generic csv export admin action.
        based on http://djangosnippets.org/snippets/1697/
        """
        from dynamic_forms.models import FormModelData
        if queryset.count() > 1:
            messages.error(request, "You can only export one form at a time.");
            return
        form_obj = queryset[0]
        form_data = FormModelData.objects.filter(form=form_obj)
        csv_filename = slugify("%s %s" % (form_obj.name, timezone.now()))
        header_names = []
        fields = form_obj.fields.all()
        for field in fields:
            if field.field_type in ('dynamic_forms.formfields.StartGroupField',
                                    'dynamic_forms.formfields.EndGroupField'):
                continue
            header_names.append(field.label)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % csv_filename

        writer = csv.writer(response)
        if header_names:
            writer.writerow(["Submitted",] + header_names)
        for data in form_data:
            json_value = json.loads(data.value)
            row_data = ["%s" % data.submitted.strftime("%Y-%m-%d %H:%M"),]
            for header in header_names:
                row_data.append(unicode(json_value[header]).encode("utf-8","replace"))
            writer.writerow(row_data)
        return response
    export_as_csv.short_description = description
    return export_as_csv
