from django.conf.urls import url
from . import views
app_name = 'chats'


urlpatterns = [
    url(r'^$', views.all_rooms, name="all_rooms"),
    # url(r"new/$", views.CreateChat.as_view(), name="create"),
    # url(r'token$', views.token, name="token"),
    # url(r"by/(?P<username>[-\w]+)/$",views.UserChats.as_view(),name="for_user"),
    # # url(r"by/(?P<username>[-\w]+)/(?P<pk>\d+)/$", views.ChatDetail.as_view(), name="single"),
    url(r'(?P<slug>[-\w]+)/$', views.chat_room, name="chat_room"),
    # url(r"delete/(?P<pk>\d+)/$", views.DeleteChat.as_view(), name="delete"),
    url(r'chat_message_json', views.chat_message_json, name="chat_message_json"),
    url(r'chat_thread_message_json', views.chat_thread_message_json,
        name="chat_thread_message_json"),
    url(r'chat_update_thanks', views.update_thanks, name="update_thanks"),
    url(r'chat_online_users', views.chat_online_users, name="chat_online_users"),
    url(r'all_answers', views.all_answers, name="all_answers")

]
