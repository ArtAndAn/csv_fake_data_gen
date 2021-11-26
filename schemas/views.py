from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DeleteView

from schemas.helpers import SchemaDataMixin
from schemas.models import Schema, SchemaColumn


class DataSchemas(LoginRequiredMixin, ListView):
    model = Schema
    template_name = 'schemas/schemas.html'
    login_url = '/login'

    def get_queryset(self):
        qs = Schema.objects.filter(user=self.request.user).order_by('-modified_date')
        for i in range(len(qs)):
            qs[i].modified_date = qs[i].modified_date.strftime('%d %B %Y %H:%M ')
            qs[i].number = i + 1
        return qs


class NewSchema(SchemaDataMixin, LoginRequiredMixin, View):
    login_url = '/login'

    def get(self, request):
        return render(request, 'schemas/new_schema.html')

    def post(self, request):
        form = request.POST
        columns = self.create_columns(form=form)

        form_errors = self.validate_new_schema(schema_name=form['name'], columns=columns)
        if form_errors:
            return render(request, 'schemas/new_schema.html', context=form_errors)
        else:
            self.create_schemas(form=form, columns=columns)
            return redirect('schemas')

    def create_schemas(self, form, columns):
        new_schema = Schema(schema_name=form['name'],
                            schema_separator=form['separator'],
                            schema_string_char=form['character'],
                            user=self.request.user)
        new_schema.save()
        for column, config in columns.items():
            SchemaColumn(column_name=config['column-name'],
                         column_type=config['column-type'],
                         column_order=config['column-order'],
                         column_from=config.get('column-range-from'),
                         column_to=config.get('column-range-to'),
                         schema_name=new_schema
                         ).save()


class EditSchema(SchemaDataMixin, LoginRequiredMixin, View):
    login_url = '/login'

    def get(self, request, schema_name):
        schema_conf = Schema.objects.filter(user=request.user).filter(schema_name=schema_name)
        if schema_conf:
            schema_columns = SchemaColumn.objects.filter(schema_name=schema_conf[0])
            for i in range(len(schema_columns)):
                schema_columns[i].number = i
            context = {'conf': schema_conf.first(), 'columns': schema_columns}
            return render(request, 'schemas/edit_schema.html', context=context)
        else:
            return redirect('schemas')

    def post(self, request, schema_name):
        schema_conf = Schema.objects.filter(user=request.user).filter(schema_name=schema_name)
        if not schema_conf:
            return redirect('schemas')

        new_form = request.POST
        new_schema_columns = self.create_columns(form=new_form)

        new_form_errors = self.validate_edit_schema(new_schema_name=new_form['name'],
                                                    old_schema_name=schema_conf[0].schema_name,
                                                    columns=new_schema_columns)
        if new_form_errors:
            return render(request, 'schemas/new_schema.html', context=new_form_errors)
        else:
            self.update_schema(old_schema=schema_conf[0], new_schema=new_form, new_columns=new_schema_columns)
            return redirect('schemas')

    def update_schema(self, old_schema, new_schema, new_columns):
        SchemaColumn.objects.filter(schema_name=old_schema).delete()
        old_schema.schema_name = new_schema['name']
        old_schema.schema_separator = new_schema['separator']
        old_schema.schema_string_char = new_schema['character']
        old_schema.save()

        for column, config in new_columns.items():
            SchemaColumn(column_name=config['column-name'],
                         column_type=config['column-type'],
                         column_order=config['column-order'],
                         column_from=config.get('column-range-from'),
                         column_to=config.get('column-range-to'),
                         schema_name=old_schema
                         ).save()


class DeleteSchema(LoginRequiredMixin, DeleteView):
    login_url = '/login'

    def get(self, request, **kwargs):
        self.delete(**kwargs)
        return redirect('schemas')

    def delete(self, **kwargs):
        schema_conf = Schema.objects.filter(user=self.request.user).filter(schema_name=kwargs['schema_name'])
        if not schema_conf:
            return redirect('schemas')
        SchemaColumn.objects.filter(schema_name=schema_conf[0]).delete()
        schema_conf.delete()


def data_sets(request):
    return render(request, 'schemas/data_sets.html')
