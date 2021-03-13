from django.urls import path
from django.urls.resolvers import URLPattern

from .views import (
    account_view,
)

app_name = "account"

urlpatterns = [
    path('<user_id>/',account_view, name="view"),

]