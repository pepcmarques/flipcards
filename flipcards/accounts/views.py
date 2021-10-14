# accounts/views.py
from django.contrib import auth, messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.shortcuts import redirect, render
from django.utils.http import is_safe_url, urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse

from flipcards.settings import SYSTEM_NAME
from flipcards.accounts.models import User
from flipcards.accounts.forms import LoginForm, UsersForm, UsersUpdateForm, SignupForm, ForgottenPasswordForm, \
    PasswordChangeForm
from flipcards.accounts.tokens import account_activation_token


def get_redirect_path(request):
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None
    if is_safe_url(redirect_path, request.get_host()):
        return redirect_path
    else:
        return "/"


def sign_in(request):
    if request.user.is_authenticated:
        return redirect('/')

    form = LoginForm()

    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            # correct username and password login the user
            auth.login(request, user)
            return redirect(get_redirect_path(request))
        else:
            return redirect('/')

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('/')


def build_message(request, template, user):
    current_site = get_current_site(request)
    message = render_to_string(template, {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    return message


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            #
            mail_subject = 'Activate your {0} account.'.format(SYSTEM_NAME)
            message = build_message(request, "acc_active_email.html", user)
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            #
            messages.add_message(request, messages.INFO, 'Please confirm your email address to complete the '
                                                         'registration')
            return render(request, 'home.html')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request,  'home.html',
                      {'message': "Thank you for clicking on the link. Now you can start using the system."})
    else:
        return render(request, 'home.html', {'message': 'Activation link is invalid!'})


@sensitive_post_parameters()
@csrf_protect
@never_cache
def forgotten_password(request):
    if request.method == 'POST':
        form = ForgottenPasswordForm(request.POST)
        if form.is_valid():
            user = User.objects.filter(email=form.cleaned_data['email'])
            if user:
                user = user[0]  # first and only user
                #
                mail_subject = 'Password reset for your {0} account.'.format(SYSTEM_NAME)
                message = build_message(request, "acc_reset_password.html", user)
                to_email = form.cleaned_data.get('email')
                email = EmailMessage(mail_subject, message, to=[to_email])
                email.send()
                #
            return redirect('accounts:forgotten_password_done')
    else:
        form = ForgottenPasswordForm()
    return render(request, 'forgotten.html', {'form': form})


def profile(request, user_id):
    return update_user(request, user_id)


@user_passes_test(lambda u: u.is_superuser)
def list_users(request):
    users = User.objects.order_by('email')
    return render(request, 'users.html', {'users': users})


@user_passes_test(lambda u: u.is_superuser)
def create_user(request):
    form = UsersForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('list_users')
    return render(request, 'user-form.html', {'form': form})


@login_required()
def update_user(request):
    user = User.objects.get(id=request.user.id)
    form = UsersUpdateForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        return redirect(reverse('base:home'))
    return render(request, 'user-form.html', {'form': form, 'user': user})


def password_change(request, user_id):
    if not request.user.is_superuser:
        if request.user.id != user_id:
            return redirect(reverse('base:index'))
    user = User.objects.get(id=user_id)
    form = PasswordChangeForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        login(request, user)
        return render(request,  'home.html', {'message': "Password was set!"})
    return render(request, 'password_change.html', {'form': form, 'user': user})


@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('list_users')
    return render(request, 'user-delete-confirm.html', {'user': user})
