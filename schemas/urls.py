from . import views
from django.urls import path

urlpatterns = [
    path('schemas', views.data_schemas, name='schemas')
]
