import json
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views.decorators.csrf import requires_csrf_token
from django.forms import ValidationError
from django.contrib.auth import authenticate, views, update_session_auth_hash
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core import serializers

from chats.models import ChatRoom, ChatMessage, ChatThreadMessage, ChatThread

from . import forms


def login(request):
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            auth_login(request, user)
            return redirect('/')
    else:
        form = forms.LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            auth_login(request, user)
            return redirect('/')
    else:
        form = forms.SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def superuser_only(function):
    def _inner(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return function(request, *args, **kwargs)
    return _inner


@superuser_only
def view_profile(request):
    args = {'user': request.user}
    return render(request, 'accounts/profile.html', args)


@login_required
@transaction.atomic
def edit_profile(request):
    page = "profile"
    display_name_form = forms.EditDisplayNameForm(instance=request.user)
    grad_year_form = forms.EditGradYearForm(instance=request.user.profile)

    if request.method == "POST":
        grad_year_changed = int(
            request.POST['grad_year']) != request.user.profile.grad_year
        name_changed = request.POST['username'] != request.user.username

        if name_changed:
            display_name_form = forms.EditDisplayNameForm(
                request.POST, instance=request.user)
            original_username = request.user.username
            if display_name_form.is_valid():
                display_name_form.save()
                # update grad year only if display name is valid
                if grad_year_changed:
                    grad_year_form = forms.EditGradYearForm(
                        request.POST, instance=request.user.profile)
                    if grad_year_form.is_valid():
                        grad_year_form.save()
                messages.success(request, 'Your profile has been updated.')
            else:
                messages.error(request, 'Your profile has not been updated.')
                # used to reset username that is displayed to user on update failure
                request.user.username = original_username
        # if display name isn't changed
        elif grad_year_changed:
            grad_year_form = forms.EditGradYearForm(
                request.POST, instance=request.user.profile)
            if grad_year_form.is_valid():
                grad_year_form.save()
                messages.success(request, 'Your profile has been updated.')

    print(request.user.username)
    return render(request, 'home/home-template.html', {'display_name_form': display_name_form, 'grad_year_form': grad_year_form, 'page': page})


@login_required
@transaction.atomic
def edit_account(request):
    page = "account_settings"
    email_form = forms.EditEmailForm(instance=request.user)
    password_form = forms.EditPasswordForm(user=request.user)
    if request.method == "POST":
        password_changed = (request.POST['old_password'] != "") & (
            request.POST['new_password1'] != "") & (request.POST['new_password2'] != "")
        email_changed = request.POST['email'] != request.user.email
        print(email_form.is_valid())
        print(password_form.is_valid())
        if email_changed & ~password_changed:
            email_form = forms.EditEmailForm(
                request.POST, instance=request.user)
            if email_form.is_valid():
                email_form.save()
                messages.success(request, 'Your account has been updated.')
            else:
                messages.error(request, 'Your account has not been updated.')

        if password_changed & ~email_changed:
            password_form = forms.EditPasswordForm(
                data=request.POST, user=request.user)
            if password_form.is_valid():
                update_session_auth_hash(request, password_form.user)
                password_form.save()
                messages.success(request, 'Your account has been updated.')
            else:
                messages.error(request, 'Your account has not been updated.')

        if email_changed & password_changed:
            email_form = forms.EditEmailForm(
                request.POST, instance=request.user)
            password_form = forms.EditPasswordForm(
                data=request.POST, user=request.user)
            if email_form.is_valid() & password_form.is_valid():
                email_form.save()
                update_session_auth_hash(request, password_form.user)
                password_form.save()
                messages.success(request, 'Your account has been updated.')
            else:
                messages.error(request, 'Your account has not been updated.')

    return render(request, 'home/home-template.html', {'email_form': email_form, 'password_form': password_form, 'page': page})


@login_required
def view_questions(request):
    # We need to look into querying the questions
    page = "view_questions"

    get_all_rooms = ChatRoom.objects.all()

    json_all_rooms = json.loads(
        serializers.serialize('json', ChatRoom.objects.all()))

    get_all_messages_asked = list(ChatMessage.objects.filter(
        thread=True, user=request.user).values())

    for item in get_all_messages_asked:

        if item['thread']:
                # This adds a section to threads and gives the length of the Chat Thread Messages found in the thread
            chat_thread_room = ChatThread.objects.get(thread_id=item['id'])
            thread_size = serializers.serialize(
                'json', ChatThreadMessage.objects.filter(chat_thread=chat_thread_room))
            item['chat_thread_respose_total'] = len(json.loads(thread_size))

    get_all_messages_asked.reverse()

    # json_all_messages_asked = serializers.serialize(
    #     'json', ChatMessage.objects.filter(thread=True, user=request.user))

    # print("chat room", json_all_rooms)

    # print(json_all_messages_asked)

    return render(request, 'home/home-template.html', {'page': page, 'all_rooms': get_all_rooms, 'all_messages': get_all_messages_asked})


def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(data=request.POST, user=request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('/accounts/profile')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'accounts/change_password.html', {'form': form})


@requires_csrf_token
def add_pistachio(request, pk, direction):
    user = User.objects.get(pk=pk)
    print(direction)
    if \
            (direction == "up"):
        user.profile.rating += 1
    if (direction == "down"):
        user.profile.rating -= 1
    user.save()
    rating = json.dumps(user.profile.rating)
    return JsonResponse({"success": True, "rating": rating}, safe=False)


# @huyen Let's say a user updates their display name and grad year at the same time, but the display name they chose is already taken, and hence an error of "A user with that username already exists." will appear. Should the grad year still be updated? As in, should we show both "Your profile has been updated!" and the error message as bubbles on the top right?
