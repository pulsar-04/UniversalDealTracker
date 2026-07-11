from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import CustomUserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django_ratelimit.core import is_ratelimited

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()


            login(request, user)

            messages.success(request, f'Добре дошъл, {user.username}! Успешна регистрация.')
            return redirect('car_list')
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})


def custom_login(request):
    is_blocked = is_ratelimited(request, group='login_failed', key='ip', rate='5/15m', increment=False)
    if is_blocked:
        return render(request, 'users/403_ratelimit.html', status=403)

    if request.user.is_authenticated:
        return redirect('car_list')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if remember_me:
                request.session.set_expiry(2592000)
            else:
                request.session.set_expiry(0)

            return redirect('car_list')
        else:
            is_ratelimited(request, group='login_failed', key='ip', rate='5/15m', increment=True)
            messages.error(request, 'Грешно потребителско име или парола!')
            return render(request, 'users/login.html', {'submitted_username': username})

    return render(request, 'users/login.html')

@login_required
def profile_settings(request):
    if request.method == 'POST':

        new_username = request.POST.get('username')
        new_email = request.POST.get('email')

        receive_emails = request.POST.get('receive_emails') == 'on'

        from django.contrib.auth.models import User
        if User.objects.filter(username=new_username).exclude(pk=request.user.pk).exists():
            messages.error(request, 'Това потребителско име вече е заето!')
        else:
            request.user.username = new_username
            request.user.email = new_email
            request.user.save()

            request.user.profile.receive_emails = receive_emails
            request.user.profile.save()

            messages.success(request, 'Профилът ти беше успешно обновен!')
            return redirect('profile_settings')

    return render(request, 'users/settings.html')


@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Профилът ти беше изтрит завинаги. Ще се радваме да се върнеш отново!')
        return redirect('landing')

    return redirect('profile_settings')