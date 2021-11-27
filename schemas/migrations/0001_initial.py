# Generated by Django 3.2.9 on 2021-11-27 14:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FakeData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=500)),
                ('data', models.TextField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Schema',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schema_name', models.CharField(max_length=500, unique=True)),
                ('schema_separator', models.CharField(max_length=100)),
                ('schema_string_char', models.CharField(max_length=100)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SchemaColumn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('column_name', models.CharField(max_length=10000)),
                ('column_type', models.CharField(max_length=50)),
                ('column_order', models.IntegerField()),
                ('column_from', models.IntegerField(null=True)),
                ('column_to', models.IntegerField(null=True)),
                ('schema_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schemas.schema')),
            ],
        ),
        migrations.CreateModel(
            name='DataSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField()),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='Processing', max_length=50)),
                ('csv_file', models.FileField(upload_to='')),
                ('schema', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schemas.schema')),
            ],
        ),
    ]
