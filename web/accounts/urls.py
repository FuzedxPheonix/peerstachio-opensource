from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views, forms

# from peerstachio.accounts import views as views

app_name = 'accounts'

urlpatterns = [
    url(r"login/$", auth_views.login, {'template_name': 'accounts/login.html',
                                       'authentication_form': forms.LoginForm}, name='login'),
    url(r"logout/$", auth_views.LogoutView.as_view(), name="logout"),
    url(r"signup/$", views.signup, name="signup"),
    url(r"profile/$", views.view_profile, name="view_profile"),
    url(r"profile/edit/$", views.edit_profile, name="edit_profile"),
    url(r"questions/$", views.view_questions, name="view_questions"),
    url(r"edit/$", views.edit_account, name="edit_account"),
    url(r"change-password/$", views.change_password, name="change_password"),
    url(r"add-pistachio/(?P<pk>\d+)/(?P<direction>[-\w]+)/",
        views.add_pistachio, name="add_pistachio"),

]
