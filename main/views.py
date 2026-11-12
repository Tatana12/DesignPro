from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Application, User, Category
from .forms import RegisterForm, LoginForm, ApplicationCreateForm, ChangeStatusForm, CategoryForm
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
        return redirect('dashboard')

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
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, 'main/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('dashboard')

    error_message = None

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_staff:
                    return redirect('admin_dashboard')
                return redirect('dashboard')
            else:
                error_message = 'Неверный логин или пароль.'
    else:
        form = LoginForm()

    return render(request, 'main/login.html', {'form': form, 'error_message': error_message})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('index')


@login_required
def create_application(request):
    if request.method == 'POST':
        form = ApplicationCreateForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.status = 'new'
            application.save()
            return redirect('dashboard')
    else:
        form = ApplicationCreateForm()

    return render(request, 'main/create_application.html', {'form': form})


@login_required
def dashboard(request):
    status_filter = request.GET.get('status', '')
    applications = Application.objects.filter(user=request.user).order_by('-created_at')

    if status_filter in ['new', 'in_progress', 'completed']:
        applications = applications.filter(status=status_filter)

    context = {
        'applications': applications,
        'status_filter': status_filter,
    }
    return render(request, 'main/dashboard.html', context)


@login_required
def delete_application(request, pk):
    application = get_object_or_404(Application, pk=pk, user=request.user)

    if application.status != 'new':
        return HttpResponseForbidden('Нельзя удалить заявку, статус которой уже изменён администратором.')

    if request.method == 'POST':
        application.delete()
        return redirect('dashboard')

    return render(request, 'main/delete_application.html', {'application': application})


@staff_member_required(login_url='login')
def admin_dashboard(request):
    applications = Application.objects.all().order_by('-created_at')
    return render(request, 'main/admin_dashboard.html', {'applications': applications})


@staff_member_required(login_url='login')
def change_status(request, pk):
    application = get_object_or_404(Application, pk=pk)

    if application.status != 'new':
        return HttpResponseForbidden('Смена статуса возможна только для заявок со статусом «Новая».')

    if request.method == 'POST':
        form = ChangeStatusForm(request.POST, request.FILES)
        if form.is_valid():
            application.status = form.cleaned_data['status']
            if application.status == 'in_progress':
                application.comment = form.cleaned_data['comment']
            elif application.status == 'completed':
                application.design_image = form.cleaned_data['design_image']
            application.save()
            return redirect('admin_dashboard')
    else:
        form = ChangeStatusForm()

    return render(request, 'main/change_status.html', {'form': form, 'application': application})

@staff_member_required(login_url='login')
def manage_categories(request):
    categories = Category.objects.all().order_by('name')

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_categories')
    else:
        form = CategoryForm()

    return render(request, 'main/manage_categories.html', {
        'categories': categories,
        'form': form,
    })


@staff_member_required(login_url='login')
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        category.delete()
        return redirect('manage_categories')

    return render(request, 'main/delete_category.html', {'category': category})
