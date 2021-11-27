from . import views
from django.urls import path

urlpatterns = [
    path('schemas', views.DataSchemas.as_view(), name='schemas'),
    path('new-schema', views.NewSchema.as_view(), name='new_schema'),
    path('edit-schema/<str:schema_name>', views.EditSchema.as_view(), name='edit_schema'),
    path('delete-schema/<str:schema_name>', views.DeleteSchema.as_view(), name='delete_schema'),
    path('data-sets/<str:schema_name>', views.DataSetsView.as_view(), name='data_sets'),
    path('new-data-set/<str:schema_name>/<int:rows>', views.NewDataSetView.as_view(), name='new_data_set'),
    path('add-fake-data', views.AddFakeData.as_view(), name='add_fake_data'),
]
