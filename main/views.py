from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import Application, User
from .forms import RegisterForm, LoginForm


def index(request):
    in_progress_count = Application.objects.filter(status='in_progress').count()
    completed_apps = Application.objects.filter(status='completed').order_by('-created_at')[:4]

    context = {
        'in_progress_count': in_progress_count,
        'completed_apps': completed_apps,
    }
    return render(request, 'main/index.html', context)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                full_name=form.cleaned_data['full_name'],
            )
            login(request, user)
            return redirect('index')
    else:
        form = RegisterForm()

    return render(request, 'main/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    error_message = None

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')  # Позже заменим на редирект в личный кабинет
            else:
                error_message = 'Неверный логин или пароль.'
    else:
        form = LoginForm()

    return render(request, 'main/login.html', {'form': form, 'error_message': error_message})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('index')
