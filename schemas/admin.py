from django.contrib import admin

from schemas.models import SchemaColumn, Schema, DataSet, FakeData

admin.site.register(SchemaColumn)
admin.site.register(Schema)
admin.site.register(DataSet)
admin.site.register(FakeData)
