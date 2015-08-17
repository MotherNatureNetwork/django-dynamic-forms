# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, FormView, TemplateView
from django.http import HttpResponse, HttpResponseRedirect

from dynamic_forms.actions import action_registry
from dynamic_forms.forms import FormModelForm
from dynamic_forms.models import FormModelData, FormModel
from dynamic_forms.utils import is_old_style_action


class DynamicFormView(FormView):

    form_class = FormModelForm

    def dispatch(self, request, *args, **kwargs):
        form_id = int(kwargs['form_id'])
        try:
            self.form_model = FormModel.objects.get(id=form_id)
        except:
            return HttpResponse('')
        return super(DynamicFormView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DynamicFormView, self).get_context_data(**kwargs)
        context.update({
            'model': self.form_model,
            'name': self.form_model.name,
        })
        return context

    def get_form_kwargs(self):
        kwargs = super(DynamicFormView, self).get_form_kwargs()
        kwargs['model'] = self.form_model
        return kwargs

    def get_success_url(self):
        """
        If the ``dynamic_form_store_database`` action is active for the current
        form, include the ``display_key`` for the newly created data set.
        """
        return self.request.META.get('HTTP_REFERER','/')

    def get_template_names(self):
        if self.form_model.display:
            return self.form_model.form_template
        return 'dynamic_forms/blank.html'

    def form_valid(self, form):
        """
        Instantiates an empty dict ``self.action_results`` that takes the
        return values of every action that is called, unless the return value
        of that action is ``None``.
        """
        self.action_results = {}
        for actionkey in self.form_model.actions:
            action = action_registry.get(actionkey)
            if action is None:
                continue
            args = (self.form_model, form)

            if not is_old_style_action(action):
                args = args + (self.request,)

            self.action_results[actionkey] = action(*args)
        messages.success(self.request,
            _('Thank you for submitting this form.'))
        return super(DynamicFormView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request,
            _('An error occurred during submitting this form.'))
        return super(DynamicFormView, self).form_invalid(form)


class DynamicTemplateView(TemplateView):

    def dispatch(self, request, *args, **kwargs):
        self.form_model = self.kwargs.pop('model')
        return super(DynamicTemplateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        If a ``display_key`` query parameter is given and the key belongs to a
        FormModel that has ``allow_display=True``, add the data to the normal
        Django `TemplateView` context.
        """
        context = super(DynamicTemplateView, self).get_context_data(**kwargs)
        try:
            display_key = self.request.GET.get('display_key')
            data = FormModelData.objects.get(display_key=display_key)
            context.update({
                'data': data,
            })
        except FormModelData.DoesNotExist:
            pass
        return context

    def get_template_names(self):
        return self.form_model.success_template


class DynamicDataMixin(object):

    slug_field = 'display_key'
    slug_url_kwarg = 'display_key'
    template_name_404 = 'dynamic_forms/data_set_404.html'

    def get(self, request, *args, **kwargs):
        try:
            return super(DynamicDataMixin, self).get(request, *args, **kwargs)
        except Http404:
            return self.render_404({})

    def get_template_names_404(self):
        return [self.template_name_404]

    def render_404(self, context=None, **response_kwargs):
        ctx = {
            'display_key': self.kwargs.get(self.slug_url_kwarg, None)
        }
        if context:
            ctx.update(context)
        return self.response_class(request=self.request,
            template=self.get_template_names_404(), context=ctx, status=404,
            **response_kwargs)


class DynamicDataSetDetailView(DynamicDataMixin, DetailView):

    model = FormModelData
    template_name = 'dynamic_forms/data_set.html'


def form_handler(request):
    if request.method == 'POST':
        form = FormModelForm(request.POST)
        hmapped_data = form.get_mapped_data()
        value = json.dumps(mapped_data, cls=DjangoJSONEncoder)
        data = FormModelData.objects.create(form=form_model, value=value)
        return HttpResponse(data)
    return HttpResponse('YO')

def get_form(request, form_id=0):
    if request.method == 'GET':
        try:
            form_model = FormModel.objects.get(id=form_id)
        except:
            raise Http404
        kwargs = {'model': form_model}
        viewfunc = DynamicFormView.as_view(model=form_model)
        new_resp = viewfunc(request, model=form_model)
        return new_resp.render()
    raise Http404


data_set_detail = DynamicDataSetDetailView.as_view()
