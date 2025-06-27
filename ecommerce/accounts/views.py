from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

from .forms import RegisterForm
from .models import Account


# Create your views here.

def register(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split('@')[0]

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                username=username
            )
            user.phone_number = phone_number
            user.save()

            messages.success(request, 'You have registered successfully.')

            return redirect('register')
        else:
            pass

    data = {
        'form': form,
    }

    return render(
        request,
        'accounts/register.html',
        data
    )

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)

            return redirect('home')
        else:
            messages.error(request, 'Invalid user credentials.')

            return redirect('login')

    return render(
        request,
        'accounts/login.html'
    )

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'Has logged out.')

    return redirect('login')