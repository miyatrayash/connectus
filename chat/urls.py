from .views import home
from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    url(r'^home', home,name="Home"),
]

urlpatterns += staticfiles_urlpatterns()