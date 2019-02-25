from django.shortcuts import render

# Create your views here.
from django.views import generic
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import SelectRelatedMixin, SuperuserRequiredMixin
from django.urls import reverse_lazy
from django.http import Http404

from . import forms
from . import models
import json
from .models import ChatRoom, ChatMessage, ChatThreadMessage, ChatThread, ThankMessageChat, ThankMessageChatThread, UserRoomOnline
from django.core import serializers
from django.utils.safestring import mark_safe
from django.http import JsonResponse
from django.http import HttpResponse

from django.views.decorators.csrf import requires_csrf_token
from django.http import JsonResponse

from django.contrib.auth.models import User

from django.db import connection


def my_custom_sql():
    with connection.cursor() as cursor:
        cursor.execute('select * from chats_userroomonline INNER JOIN accounts_profile on accounts_profile.id = chats_userroomonline.user_id INNER JOIN (SELECT id, username from auth_user ) a on a.id =  chats_userroomonline.user_id where chats_userroomonline.is_online = true;')
        rows = cursor.fetchall()

        result = []
        keys = ('id', 'is_online', 'chat_room_id', 'user_id', 'ID', 'rating', 'grad_year', 'avatar', 'said_thanks', 'user_id', 'auth_id', 'username',)

        for row in rows:
            result.append(dict(zip(keys, row)))

            json_data = json.dumps(result)

    return json_data


def all_rooms(request):
    """
    This view request will get a list of the room objects

    :param request:
    :return:
    """
    # Rooms: this will contain all the room objects that will have the following
    rooms = ChatRoom.objects.all()
    return render(request, 'chats/index.html', {'rooms': rooms})


def chat_room(request, slug):
    """
    The request is going to be loading in a page

    :param request:
    :param slug:
    :return:
    """
    rooms = ChatRoom.objects.all()
    room = ChatRoom.objects.get(room_name_slug=slug)

    return render(request, 'chats/chat_room.html', {
        'room': room,
        'rooms': rooms,
    })


def chat_message_json(request):
    """
    This will return a list of Chat messages object that will be loaded to the browser
    :param request:
    :return:
    """
    chat_slug = request.GET.get('slug')
    room = ChatRoom.objects.get(room_name_slug=chat_slug)

    data_user = request.user

    # This collects all the chat messages found in a chat room
    response = serializers.serialize('json', ChatMessage.objects.filter(
        chat_room=room.id),  use_natural_foreign_keys=True)

    say_thanks = []

    data_json = json.loads(response)

    for item in data_json:
        data = get_thank(item, data_user.id)

        say_thanks.append(data)

        if item['fields']['thread']:
            # This adds a section to threads and gives the length of the Chat Thread Messages found in the thread
            chat_thread_room = ChatThread.objects.get(thread_id=item['pk'])
            thread_size = serializers.serialize(
                'json', ChatThreadMessage.objects.filter(chat_thread=chat_thread_room))
            item['fields']['chat_thread_respose_total'] = len(
                json.loads(thread_size))

    count = 0

    while count < len(data_json):

        # This modifies the current array but adding the total amount of thanks and whether the user thank it or not
        data_json[count]['total_thanks'] = say_thanks[count]['total']
        data_json[count]['thanked'] = say_thanks[count]['thanked']
        count += 1

    test_response = json.dumps(data_json)

    return HttpResponse(test_response, content_type='application/json')


def chat_online_users(request):
    chat_slug = request.GET.get('slug')
    room = ChatRoom.objects.get(room_name_slug=chat_slug)
    # response = serializers.serialize('json', UserRoomOnline.objects.filter(
    #     chat_room=room.id, is_online=True),  use_natural_foreign_keys=True)

    sql_query = my_custom_sql();

    return HttpResponse(sql_query, content_type='application/json')


def all_answers(request):
    chat_slug = request.GET.get('slug')
    room = ChatRoom.objects.get(room_name_slug=chat_slug)

    response = serializers.serialize('json', ChatMessage.objects.filter(
        chat_room=room.id, thread=True),  use_natural_foreign_keys=True)

    return HttpResponse(response, content_type='application/json')


def get_thank(message, userid):
    """
    This function will be called when its loading
    :param message:
    :param userid:
    :return:
    """

    say_thanks_obj = serializers.serialize(
        'json', ThankMessageChat.objects.filter(message_id=message["pk"], thanked=True))

    json_data = json.loads(say_thanks_obj)

    thanked_person = serializers.serialize(
        'json', ThankMessageChat.objects.filter(message_id=message["pk"], user=userid))

    json_test = json.loads(thanked_person)

    is_thanked = False

    if len(json_test) > 0:

        is_thanked = json_test[0]['fields']['thanked']

    elif len(json_test) == 0:
        is_thanked = False
    else:
        is_thanked = False

    out_put = {"total": len(json_data),
               "id": message["pk"], "thanked": is_thanked}

    return out_put


def chat_thread_message_json(request):
    """
    This will return a list of chat thread message object
    :param request:
    :return:
    """
    chat_thread_slug = int(request.GET.get('slug'))

    thread_room = ChatThread.objects.get(thread_id=chat_thread_slug)

    response = serializers.serialize('json', ChatThreadMessage.objects.filter(
        chat_thread=thread_room),  use_natural_foreign_keys=True)

    data = {'slug': chat_thread_slug, 'response': response}

    return HttpResponse(json.dumps(data), content_type='application/json')


def update_thanks(request):
    """

    :param request:
    :return:
    """
    messageid = int(request.GET.get('message_id'))

    message_bool = request.GET.get('bool_test')

    if message_bool == "true":
        message_bool = True

    else:
        message_bool = False

    if (message_bool):

        chat_message_obj = ChatThreadMessage.objects.get(pk=messageid)

        data_user = request.user

        thanked_person = serializers.serialize('json',
                                               ThankMessageChatThread.objects.filter(message_id=messageid, user=data_user.id))

        json_test = json.loads(thanked_person)

        if len(json_test) > 0:
            is_thanked = not json_test[0]['fields']['thanked']

            update_thank_message = ThankMessageChatThread.objects.filter(
                message_id=messageid).update(thanked=is_thanked)

        else:
            is_thanked = True

            save_thank_message = ThankMessageChatThread(
                message_id=chat_message_obj, user=data_user, thanked=is_thanked)

            save_thank_message.save()

        say_thanks_obj = serializers.serialize('json',
                                               ThankMessageChatThread.objects.filter(message_id=messageid, thanked=True))

        json_data = json.loads(say_thanks_obj)

        out_put = {"total": len(json_data), "id": messageid,
                   "thanked": is_thanked}

        return HttpResponse(json.dumps(out_put), content_type='application/json')

    else:
        chat_message_obj = ChatMessage.objects.get(pk=messageid)
        data_user = request.user

        thanked_person = serializers.serialize('json',
                                               ThankMessageChat.objects.filter(message_id=messageid, user=data_user.id))

        json_test = json.loads(thanked_person)

        if len(json_test) > 0:
            is_thanked = not json_test[0]['fields']['thanked']

            update_thank_message = ThankMessageChat.objects.filter(
                message_id=messageid, user=data_user.id).update(thanked=is_thanked)

        else:
            is_thanked = True

            save_thank_message = ThankMessageChat(
                message_id=chat_message_obj, user=data_user, thanked=is_thanked)

            save_thank_message.save()

        say_thanks_obj = serializers.serialize(
            'json', ThankMessageChat.objects.filter(message_id=messageid, thanked=True))

        json_data = json.loads(say_thanks_obj)
        print(json_data)

        out_put = {"total": len(json_data), "id": messageid,
                   "thanked": is_thanked}

        return HttpResponse(json.dumps(out_put), content_type='application/json')
