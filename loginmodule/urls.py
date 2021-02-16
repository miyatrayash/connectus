from django.urls import path
from loginmodule.views import login, auth_view, logout,logged_in, invalid_login
from django.contrib.auth import views as auth_views
from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    url(r'^login/$', login),
    url(r'^auth/$', auth_view),
    url(r'^logout/$', logout),
    url(r'^logged_in/$', logged_in),
    url(r'^invalid_login/$', invalid_login),
]

urlpatterns += staticfiles_urlpatterns()