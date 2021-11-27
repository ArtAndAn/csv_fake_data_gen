from datetime import datetime

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView, DeleteView
from slugify import slugify

from schemas.helpers import SchemaDataMixin
from schemas.models import Schema, SchemaColumn, DataSet, FakeData
from schemas.tasks import fill_up_csv


class DataSchemas(LoginRequiredMixin, ListView):
    """
    View for showing User created DataSchemas if they exists or
    showing message that DataSchemas are not filled up yet
    (available only for logged in users)
    """
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
    """
    View for saving a new DataSchema
    (available only for logged in users)
    """
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
    """
    View for updating a DataSchema
    (available only for logged in users)
    """
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
    """
    View for deleting a DataSchema
    (available only for logged in users)
    """
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


class DataSetsView(LoginRequiredMixin, ListView):
    """
    View for showing User created DataSets filtered by specified DataSchema and their statuses if they exists or
    showing message that DataSets are not created yet
    (available only for logged in users)
    """
    model = DataSet
    template_name = 'schemas/data_sets.html'
    login_url = '/login'

    def get(self, request, **kwargs):
        self.object_list = self.get_queryset()
        if not self.object_list:
            return redirect('schemas')
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_queryset(self):
        data_schema = Schema.objects.filter(user=self.request.user).filter(
            schema_name=self.kwargs['schema_name'])
        if not data_schema:
            return data_schema
        data_sets = DataSet.objects.filter(schema=data_schema[0]).order_by('-created_date')

        for i in range(len(data_sets)):
            data_sets[i].created_date = data_sets[i].created_date.strftime('%d %B %Y %H:%M')
            data_sets[i].number = i + 1
        context = {'data_sets': data_sets, 'schema_name': data_schema[0].schema_name}
        return context


class NewDataSetView(LoginRequiredMixin, View):
    """
    View for creating new DataSets
    CSV files filling up processes executes inside Celery backend
    (available only for logged in users)
    """
    login_url = '/login'

    def get(self, request, schema_name, rows):
        schema_conf = Schema.objects.filter(user=request.user).filter(schema_name=schema_name)
        if not schema_conf:
            redirect('schemas')
        slug = slugify(f'{schema_name} {request.user} {datetime.today().strftime("%d %B %Y %H:%M:%S")}')

        separator = schema_conf[0].schema_separator
        separator_char = separator[separator.index('(') + 1:separator.index(')')]
        string_char = schema_conf[0].schema_string_char[-2]

        csv_file_path = f'media/{slug}.csv'

        fill_up_csv.delay(file_path=csv_file_path, slug=slug, separator=separator_char,
                          string_char=string_char, schema_name=schema_conf[0].schema_name, rows=rows)

        new_data_set = DataSet()
        new_data_set.slug = slug
        new_data_set.schema = schema_conf[0]
        new_data_set.csv_file.name = csv_file_path
        new_data_set.save()

        return redirect('data_sets', schema_name=schema_name)


@method_decorator(user_passes_test(lambda user: user.is_superuser), 'get')
class AddFakeData(LoginRequiredMixin, View):
    """
    View for adding fake data to DB (available only for superuser)
    """

    def get(self, request):
        if FakeData.objects.all():
            return redirect('schemas')
        full_names = ['Safia Dunn', 'Nansi Whitaker', 'Opal Duffy', 'Elize Oliver', 'Rohit Franklin', 'Bogdan Neale',
                      'Rihanna Lacey', 'Addison Jensen', 'Kodi Travers', 'Rajveer Stewart', 'Randall Spooner',
                      'Arwa Pearson', 'Ebrahim Marks', 'Sia Hughes', 'Marius Gay', 'Halimah Vance', 'Nuala Chester',
                      'Myla Lu', 'Luke Deacon', 'Inaya Portillo']
        jobs = ['Economist', 'College Professor', 'Chef', 'Hairdresser', 'Event Planner', 'Marketing Manager',
                'Dancer', 'Receptionist', 'Personal Care Aide', 'Chemist', 'Physician', 'Secretary',
                'Clinical Laboratory Technician', 'Patrol Officer', 'Anthropologist', 'Respiratory Therapist',
                'Computer Programmer', 'Housekeeper', 'Computer Systems Administrator', 'Librarian']
        emails = ['mmjjii41@googleappsmail.com', 'nicepahar@reprecentury.xyz', 'biggstick@oreple.com',
                  'flaystus@ffo.kr', 'cyndrical@yandex.cfd', 'arianasanamb@kimsangun.com', 'az0tooops@suttal.com',
                  'popovim@convoitu.com', 'cscp187918@googl.win', 'xkuzyx1999@cesitayedrive.live', 'hiwinks@codee.site',
                  'polysikk@txtsp.site', 'poppens7@sonophon.ru', 'alekseymirea@ndmlpife.com',
                  'kristencaschera@googl.win', 'olegbuba@lsnttttw.com', 'mcse47@azwd.site', 'rw93082@lsnttttw.com',
                  'arundev@gumaygo.com', 'wavewash@btcmod.com']
        domains = ['flaio.com', 'conpi.com', 'cicvu.com', 'kumbu.com', 'naraa.com', 'famzi.com', 'amaku.com',
                   'recao.com', 'sarre.com', 'dhaqo.com', 'momwi.com', 'forhe.com', 'ausqo.com', 'walmi.com',
                   'bibgu.com', 'jesnu.com', 'carqo.com', 'arike.com', 'curio.com', 'kioua.com']
        tel_numbers = ['240-638-8309', '510-656-5604', '770-296-9560', '484-926-1360', '718-616-8462', '330-916-2874',
                       '276-236-5111', '973-829-9568', '618-315-8773', '619-287-1586', '706-596-4292', '323-230-2215',
                       '843-243-7387', '815-336-0616', '210-786-4287', '818-565-7956', '979-710-3434', '773-906-3883',
                       '860-489-0984', '785-848-8457']
        companies = ['Vertex FakeData', 'Seedling FakeData', 'Type FakeData', 'Retreat FakeData', 'Monk FakeData',
                     'Physical FakeData', 'Friendly FakeData', 'Centre FakeData', 'FakeDataopolis', 'Posh FakeData',
                     'Hue FakeData', 'Cruise FakeData', 'Dome FakeData', 'Karuna FakeData', 'Painter FakeData',
                     'Incubator FakeData', 'Club FakeData', 'Round FakeData', 'Grand FakeData', 'Creative FakeData']
        full_data = [FakeData(type='Full name', data=data) for data in full_names]
        full_data += [FakeData(type='Job', data=data) for data in jobs]
        full_data += [FakeData(type='Email', data=data) for data in emails]
        full_data += [FakeData(type='Domain name', data=data) for data in domains]
        full_data += [FakeData(type='Phone number', data=data) for data in tel_numbers]
        full_data += [FakeData(type='Company name', data=data) for data in companies]
        FakeData.objects.bulk_create(full_data)
        return redirect('schemas')
