
# Create your models here.
from django.conf import settings
from django.urls import reverse
from django.db import models
import misaka
from django.utils.text import slugify

from django.db import models

from django.contrib.auth import get_user_model
User = get_user_model()

class ChatRoom(models.Model):
    """Creates an object that contains an instance of a Chat Room"""
    room_name = models.TextField()
    room_name_html = models.TextField(editable=False, null=True)
    room_name_slug = models.SlugField(allow_unicode=True, unique=True, default="")
    description = models.TextField()
    description_html = models.TextField(editable=False, null=True)

    def save(self, *args, **kwargs):
        self.name_html = misaka.html(self.room_name)
        self.description_html = misaka.html(self.description)
        self.slug = slugify(self.room_name)
        super().save(*args, **kwargs)

class ChatMessage(models.Model):
    """This contains a single message that contains the following"""
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    thread = models.BooleanField(default=False)

class ChatParticipant(models.Model):
    """Contains a user that is in a chat room"""
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    person = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

class ChatThread(models.Model):
    """Thread object that will contain all the messages"""
    thread = models.ForeignKey(ChatMessage, on_delete=models.CASCADE)

class ChatThreadMessage(models.Model):
    """Chat thread message is an message in the chat thread"""
    chat_thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

class ChatThreadParticipant(models.Model):
    """ Participant in the chat"""
    chat_thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE)
    person = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

class ThankMessageChat(models.Model):
    """Will have the amount of users who thank a chat message"""
    message_id = models.ForeignKey(ChatMessage, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    thanked = models.BooleanField(default=False)


class ThankMessageChatThread(models.Model):
    """Will have the amount of thanks on message itself"""
    message_id = models.ForeignKey(ChatThreadMessage, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    thanked = models.BooleanField(default=False)

class UserRoomOnline(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
