from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import EnvironmentalComplaint, ComplaintType, InfractionType
from .forms import EnvironmentalComplaintForm


class ComplaintListView(ListView):
    model = EnvironmentalComplaint
    template_name = 'complaints/list.html'
    context_object_name = 'complaints'
    paginate_by = 20
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('protected_area', 'sector', 'complaint_type')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_complaints'] = EnvironmentalComplaint.objects.count()
        context['complaint_types'] = ComplaintType.objects.all()
        return context


class ComplaintDetailView(DetailView):
    model = EnvironmentalComplaint
    template_name = 'complaints/detail.html'
    context_object_name = 'complaint'
    
    def get_queryset(self):
        return super().get_queryset().select_related(
            'protected_area', 'sector', 'complaint_type', 'infraction_name'
        )


class ComplaintCreateView(CreateView):
    model = EnvironmentalComplaint
    form_class = EnvironmentalComplaintForm
    template_name = 'complaints/form.html'
    success_url = reverse_lazy('complaints:list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Denuncia creada exitosamente.')
        return super().form_valid(form)


class ComplaintUpdateView(UpdateView):
    model = EnvironmentalComplaint
    form_class = EnvironmentalComplaintForm
    template_name = 'complaints/form.html'
    success_url = reverse_lazy('complaints:list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Denuncia actualizada exitosamente.')
        return super().form_valid(form)


class ComplaintDeleteView(DeleteView):
    model = EnvironmentalComplaint
    template_name = 'complaints/confirm_delete.html'
    success_url = reverse_lazy('complaints:list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Denuncia eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)
