import os

import dropbox as dropbox

from schemas.models import Schema


class SchemaDataMixin:
    """
    Mixin that validates Schema data and arranges Schema columns from form in dict
    """

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

    def validate_new_schema(self, schema_name, columns):
        if Schema.objects.filter(schema_name=schema_name).filter(user=self.request.user):
            return {'error': {
                'field': 'name',
                'message': 'You have a data schema with this name'}}
        return self.validate_columns(columns=columns)

    def validate_edit_schema(self, new_schema_name, old_schema_name, columns):
        if new_schema_name != old_schema_name and Schema.objects.filter(schema_name=new_schema_name).filter(
                user=self.request.user):
            return {'error': {
                'field': 'name',
                'message': 'You have a data schema with this name'}}
        return self.validate_columns(columns=columns)

    def validate_columns(self, columns):
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


class DropBoxFiles:
    """
    All CSV view are stored in DropBox.
    Each saving/downloading CSV file operation makes it through Dropbox.
    """
    dbx = dropbox.Dropbox('i_gfxAZNFswAAAAAAAAAAa0T69bi2r4pVnCd6MC9c4K_Ceh7kCfVBO8H-7ts0ke6')

    def get_file(self, filename):
        f, r = self.dbx.files_download(filename)
        return r.content

    def create_file(self, slug, file):
        bytes_file = bytes(file.read(), 'utf-8')
        filename = '/' + slug + '.csv'
        self.dbx.files_upload(bytes_file, filename)
