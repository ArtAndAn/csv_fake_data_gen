from django.contrib.auth.models import User
from django.db import models


class Schema(models.Model):
    schema_name = models.CharField(max_length=500, blank=False, unique=True)
    schema_separator = models.CharField(max_length=100, blank=False)
    schema_string_char = models.CharField(max_length=100, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.schema_name


class SchemaColumn(models.Model):
    column_name = models.CharField(max_length=10000, blank=False)
    column_type = models.CharField(max_length=50, blank=False)
    column_order = models.IntegerField(blank=False)
    column_from = models.IntegerField(null=True)
    column_to = models.IntegerField(null=True)
    schema_name = models.ForeignKey(Schema, on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return self.column_name
