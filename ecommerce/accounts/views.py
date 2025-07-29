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
import requests

from .forms import RegisterForm
from .models import Account
from cart.views import _cart_key
from cart.models import Cart, CartItem


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
            try:
                cart = Cart.objects.get(cart_key=_cart_key(request))
                is_cart_items_exists = CartItem.objects.filter(cart=cart).exists()

                if is_cart_items_exists:
                    cart_items = CartItem.objects.filter(cart=cart)

                    product_variations = []

                    for item in cart_items:
                        variations = item.variations.all()
                        product_variations.append(list(variations))

                    cart_items = CartItem.objects.filter(user=user)

                    ids = []
                    ex_variations = []

                    for item in cart_items:
                        variations = item.variations.all()
                        ex_variations.append(list(variations))
                        ids.append(item.id)

                    for variation in product_variations:
                        if variation in ex_variations:
                            index = ex_variations.index(variation)
                            item_id = ids[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_items = CartItem.objects.filter(cart=cart)

                            for item in cart_items:
                                item.user = user
                                item.save()

            except:
                pass

            auth.login(request, user)
            messages.success(request, 'You have successfully logged in.')

            url = request.META.get('HTTP_REFERER')

            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))

                if 'next' in params:
                    next_page = params['next']

                    return redirect(next_page)
            except:
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

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']

        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request)
            mail_subject = 'Password reset'
            body = render_to_string(
                'accounts/reset_password_email.html',
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

            messages.success(request, 'An email was sended to your email with the reset link!!')

            return redirect('login')
        else:
            messages.error(request, 'An Account with this email do not exist.')

            return redirect('forgot_password')

    return render(
        request,
            'accounts/forgot_password.html'
    )

def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password.')

        return redirect('reset_password')
    else:
        messages.error(request, 'Not valid link.')

        return redirect('login')

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']

        if password == password_confirm:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password restored successful.')

            return redirect('login')
        else:
            messages.error(request, 'Password does not match.')

            return redirect('reset_password')

    return render(
        request,
        'accounts/reset_password.html'
    )
