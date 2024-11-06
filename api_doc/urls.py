from django.urls import path, include
from . import views

app_name = 'api_doc'

urlpatterns = [
    path('', views.get_api_doc, name="api_documentation"),
]