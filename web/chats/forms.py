from django import forms

from chats import models


class ChatForm(forms.ModelForm):
    class Meta:
        fields = ("room_name", "description")
        model = models.ChatRoom

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
