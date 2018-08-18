from django.conf.urls import url

from . import views

app_name="program"
urlpatterns = [
    #url(r'^base/(?P<project_name>\w+)/$', views.load_base, name="load_base"),
    url(r'^$', views.main),
    url(r'^registration/$', views.registration_view),
    url(r'^registration_complete/$', views.registration_complete_view),
    url(r'^signup/$', views.signup_view),
    url(r'^login/$', views.login_view),
    url(r'^operation/registration/$', views.registration),
    url(r'^operation/signup/$', views.signup),
    url(r'^operation/login/$', views.login),
    url(r'^operation/logout/$', views.logout),
    url(r'^operation/delete_program/$', views.delete_program),
]
