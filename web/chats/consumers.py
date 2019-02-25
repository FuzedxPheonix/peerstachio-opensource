# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

import json


from .models import ChatRoom, ChatMessage, ChatThread, ChatThreadMessage, UserRoomOnline, User
from django.core import serializers

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


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['slug']

        self.room_group_name = 'chats_%s' % self.room_name


        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        self.online = await database_sync_to_async(self.is_online)()


        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group

        self.offline = await database_sync_to_async(self.is_offline)()


        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_json = text_data_json['message']

        if text_data_json['thread_obj']:
            thread_room = ChatThread.objects.get(thread_id=text_data_json['slug'])

            save_thread_chat_message = ChatThreadMessage(chat_thread=thread_room, message=message_json,user=self.scope["user"])
            save_thread_chat_message.save()

            serialized_obj = serializers.serialize('json', [save_thread_chat_message, ], use_natural_foreign_keys=True)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message_obj': serialized_obj, 'thread_obj': True
                }
            )

        else:

            if text_data_json['isThread']:
                room = ChatRoom.objects.get(room_name_slug=self.room_name)
                save_message_chat = ChatMessage(message=message_json, user=self.scope["user"], chat_room=room, thread=True)
                save_message_chat.save()
                save_thread = ChatThread(thread=save_message_chat)
                save_thread.save()

                serialized_obj = serializers.serialize('json', [save_message_chat, ], use_natural_foreign_keys=True)

                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message_obj': serialized_obj,
                        'thread_obj': False,
                        'create_thread': True,
                        'slug': save_message_chat.id
                    }
                )

            else:
                room = ChatRoom.objects.get(room_name_slug=self.room_name)
                save_message_chat = ChatMessage(message=message_json, user=self.scope["user"], chat_room=room,)
                save_message_chat.save()

                serialized_obj = serializers.serialize('json', [save_message_chat, ], use_natural_foreign_keys=True)

                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message_obj': serialized_obj,
                        'thread_obj': False,
                        'create_thread': False
                    }
                )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message_obj']

        if event['thread_obj']:
            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'message_obj': message, 'thread_obj': True
            }))

        else:

            if event['create_thread']:

                # Send message to WebSocket
                await self.send(text_data=json.dumps({
                    'message_obj': message,
                    'thread_obj': False,
                    'slug': event['slug'],
                    'is_thread': True
                }))
            else:
                # Send message to WebSocket
                chat_room_query = ChatRoom.objects.get(room_name_slug=self.room_name)
                # get_all_online_users = serializers.serialize('json', UserRoomOnline.objects.filter(chat_room=chat_room_query, is_online=True), use_natural_foreign_keys=True)
                get_all_online_users = my_custom_sql()

                await self.send(text_data=json.dumps({
                    'message_obj': message, 'thread_obj': False, 'is_thread': False, 'all_online_users': get_all_online_users
                }))

    def is_online(self):
        chat_room_query = ChatRoom.objects.get(room_name_slug=self.room_name)

        user_exists_in_room = serializers.serialize('json', UserRoomOnline.objects.filter(user=self.scope["user"], chat_room=chat_room_query))


        if len(json.loads(user_exists_in_room)) == 0:
            create_user_online = UserRoomOnline(user=self.scope["user"], chat_room=chat_room_query, is_online=True)
            create_user_online.save()
        else:
            get_user_online = UserRoomOnline.objects.get(user=self.scope["user"], chat_room=chat_room_query)
            get_user_online.is_online = True
            get_user_online.save(update_fields=['is_online'])

        return User.objects.all()[0]

    def is_offline(self):
        chat_room_query = ChatRoom.objects.get(room_name_slug=self.room_name)
        get_user_online = UserRoomOnline.objects.get(user=self.scope["user"], chat_room=chat_room_query)

        get_user_online.is_online = False
        get_user_online.save(update_fields=['is_online'])

        return User.objects.all()[0]




    # @database_sync_to_async
    # def update_user_incr(self, user):
    #     UserProfile.objects.filter(pk=user.pk).update(online=F('online') + 1)
    #
    # @database_sync_to_async
    # def update_user_decr(self, user):
    #     UserProfile.objects.filter(pk=user.pk).update(online=F('online') - 1)