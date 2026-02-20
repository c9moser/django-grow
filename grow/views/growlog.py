from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from django.http import HttpRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView
from grow.forms.growlog import GrowlogForm, GrowlogStrainFormSet  # noqa: F401
# from django.urls import reverse

from ..settings import GROW_TEMPLATES
from ..growapi.models import Growlog, GrowlogEntry, GrowlogStrain
from ._base import BaseView


class GrowlogDetailView(BaseView):
    template_name = GROW_TEMPLATES['grow/growlog/detail']

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        growlog = get_object_or_404(Growlog, pk=pk)
        growlog_strains = GrowlogStrain.objects.filter(growlog=growlog).order_by(
            'strain__name', 'strain__breeder__name')
        entries = GrowlogEntry.objects.filter(growlog=growlog).order_by('-timestamp')
        context = {
            'growlog': growlog,
            'growlog_strains': growlog_strains,
            'entries': entries,
        }
        return render(request, self.template_name, context)


class GrowlogCreateView(LoginRequiredMixin, CreateView):
    model = Growlog
    form_class = GrowlogForm
    template_name = GROW_TEMPLATES['grow/growlog/create']
    parent_template_name = GROW_TEMPLATES['grow/growlog/form']

    def get_success_url(self) -> str:
        return reverse('grow:growlog-detail', kwargs={'pk': self.instance.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['strains'] = GrowlogStrainFormSet(queryset=GrowlogStrain.objects.none())
        context['parent_template'] = self.parent_template_name
        return context

    def form_valid(self, form):
        growlog: Growlog = form.save(commit=False)
        growlog.grower = self.request.user
        growlog.save()
        self.instance = growlog
        return super().form_valid(form)


class GrowlogUpdateView(LoginRequiredMixin, UpdateView):
    model = Growlog
    form_class = GrowlogForm
    template_name = GROW_TEMPLATES['grow/growlog/update']
    parent_template_name = GROW_TEMPLATES['grow/growlog/form']

    def get_success_url(self) -> str:
        return reverse('grow:growlog-detail', kwargs={'pk': self.instance.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['strains'] = GrowlogStrainFormSet(instance=self.object)
        context['parent_template'] = self.parent_template_name
        return context


class GrowlogDeleteView(LoginRequiredMixin, DeleteView):
    model = Growlog
    template_name = GROW_TEMPLATES['grow/growlog/delete']

    def get_success_url(self) -> str:
        return reverse('grow:user-info')

    def post(self, request: HttpRequest, pk, **kwargs) -> HttpResponse:
        growlog = get_object_or_404(Growlog, pk=pk)  # check if growlog exists
        if growlog.grower != request.user:
            return HttpResponse(status=403)  # forbid deletion if user is not the grower
        return super().post(request, pk=pk, **kwargs)
