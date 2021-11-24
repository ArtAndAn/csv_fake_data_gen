from . import views
from django.urls import path

urlpatterns = [
    path('schemas', views.data_schemas, name='schemas'),
    path('new-schema', views.new_schema, name='new_schema'),
    path('data-sets', views.data_sets, name='data_sets'),
]
