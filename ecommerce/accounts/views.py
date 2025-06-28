from base64 import urlsafe_b64encode
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

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

            current_site = get_current_site(request)
            mail_subject = 'Account activation'
            body = render_to_string(
                'accounts/activation_link.html',
                {
                    'user': user,
                    'domain': current_site,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                }
            )

            print(body)

            send_email = EmailMessage(subject=mail_subject, body=body, to=[email])
            send_email.send()

            #messages.success(request, 'You have registered successfully.')

            return redirect('accounts/login?command=verification&email=' + email)
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
            messages.success(request, 'You have successfully logged in.')

            return redirect('dashboard')
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

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Account activated!!')

        return redirect('login')
    else:
        messages.error(request, 'Invalid activation.')

        return redirect('register')

@login_required(login_url='login')
def dashboard(request):
    return render(
        request,
        'accounts/dashboard.html'
    )

def redirect_to_dashboard(request):
    return redirect('dashboard')
