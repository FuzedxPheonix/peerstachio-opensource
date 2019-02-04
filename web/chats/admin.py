from django.contrib import admin
from .models import ChatRoom, ChatMessage, ChatParticipant, ChatThread, ChatThreadMessage, ChatThreadParticipant, ThankMessageChat, ThankMessageChatThread, UserRoomOnline

# Register your models here.
myModel = [ChatRoom, ChatMessage, ChatParticipant, ChatThread, ChatThreadMessage, ChatThreadParticipant, ThankMessageChat, ThankMessageChatThread, UserRoomOnline]

admin.site.register(myModel)
