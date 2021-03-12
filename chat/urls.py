from django.urls import path
from .views import home
from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('/home', home,name="home"),
]

urlpatterns += staticfiles_urlpatterns()