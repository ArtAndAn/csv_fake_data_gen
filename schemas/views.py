from time import strptime, strftime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView

from schemas.models import Schema, SchemaColumn


class DataSchemas(LoginRequiredMixin, ListView):
    model = Schema
    template_name = 'schemas/schemas.html'

    def get_queryset(self):
        qs = Schema.objects.filter(user=self.request.user)
        for schema in qs:
            schema.modified_date = schema.modified_date.strftime('%d %B %Y %H:%M ')
        return qs


class NewSchema(LoginRequiredMixin, View):
    login_url = '/login'

    def get(self, request):
        return render(request, 'schemas/new_schema.html')

    def post(self, request):
        form = request.POST
        columns = self.create_columns(form=form)

        form_errors = self.validate_data(form=form, columns=columns)
        if form_errors:
            return render(request, 'schemas/new_schema.html', context=form_errors)
        else:
            self.create_schemas(form=form, columns=columns)
            return redirect('schemas')

    def validate_data(self, form, columns):
        if Schema.objects.filter(schema_name=form['name']).filter(user=self.request.user):
            return {'error': {
                'field': 'name',
                'message': 'You have a data schema with this name'}}
        order = []
        for column, config in columns.items():
            if int(config['column-order']) > len(columns) or int(config['column-order']) <= 0:
                return {'error': {
                    'field': 'column-order',
                    'message': 'Column order can\'t be bigger than columns quantity or lower than 1'}}
            elif config['column-order'] in order:
                return {'error': {
                    'field': 'column-order',
                    'message': 'You can\'t give same order for different columns'}}
            elif int(config.get('column-range-from', 1)) >= int(config.get('column-range-to', 2)):
                return {'error': {
                    'field': 'column-range',
                    'message': 'Range "From" cannot be bigger than range "To"'}}
            order.append(config['column-order'])

    def create_columns(self, form):
        columns = {}
        for field in form.keys():
            if 'column' in field:
                col_number = field[-1]
                if col_number not in columns.keys():
                    columns[col_number] = {field[:-2]: form[field]}
                else:
                    columns[col_number].update({field[:-2]: form[field]})
        return columns

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


def edit_schema(request):
    return render(request, 'schemas/edit_schema.html')


def delete_schema(request):
    return render(request, 'schemas/delete_schema.html')


def data_sets(request):
    return render(request, 'schemas/data_sets.html')
