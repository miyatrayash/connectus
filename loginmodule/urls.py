from django.urls import path
from loginmodule.views import login, auth_view, logout,logged_in, invalid_login,home_screen, sign_up, register,contact_us
from django.contrib.auth import views as auth_views
from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    url(r'^login', login,name="Logins"),
    url(r'^register', register),
    url(r'^auth', auth_view),
    url(r'^logout', logout),
    url(r'^logged_in', logged_in),
    url(r'^invalid_login', invalid_login),
    url(r'^sign_up',sign_up),
    url(r'^', home_screen,name="Home"),
    url(r'^contact_us',contact_us,name="contact_us"),

]

urlpatterns += staticfiles_urlpatterns()