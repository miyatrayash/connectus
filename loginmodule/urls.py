from django.urls import path
from loginmodule.views import login, logout,home_screen, sign_up, contact_us
from django.contrib.auth import views as auth_views
from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    url(r'^login', login,name="login"),
    url(r'^logout', logout,name="log_out"),
    url(r'^sign_up',sign_up,name="sign_up"),
    url(r'^$', home_screen,name="home_screen"),
    url(r'^contact_us',contact_us,name="contact_us"),

]

urlpatterns += staticfiles_urlpatterns()