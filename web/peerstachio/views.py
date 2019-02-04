from django.views.generic import TemplateView
from django.shortcuts import render

from django.views import generic
from chats.models import ChatRoom
from django.http import JsonResponse, HttpResponse
from django.core import serializers


class HomePage(TemplateView):
    template_name = "home/home-template.html"


def index(request):
    """View function for home page of site."""
    rooms = ChatRoom.objects.all()
    page = "home"
    return render(request, 'home/home-template.html', {'rooms': rooms, 'page': page})


def home_json(request):
    rooms = serializers.serialize('json', ChatRoom.objects.all())
    return HttpResponse(rooms, content_type='application/json')
    # return JsonResponse(rooms, safe=False)
