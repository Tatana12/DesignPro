from django.shortcuts import render
from .models import Application


def index(request):
    in_progress_count = Application.objects.filter(status='in_progress').count()
    completed_apps = Application.objects.filter(status='completed').order_by('-created_at')[:4]

    context = {
        'in_progress_count': in_progress_count,
        'completed_apps': completed_apps,
    }
    return render(request, 'main/index.html', context)
