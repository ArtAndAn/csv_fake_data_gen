from django.contrib import admin

from schemas.models import SchemaColumn, Schema

admin.site.register(SchemaColumn)
admin.site.register(Schema)
