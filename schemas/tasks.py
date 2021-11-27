import csv
import datetime
import random
import string

from celery import shared_task

from .models import FakeData, SchemaColumn, DataSet


@shared_task
def fill_up_csv(file_path, slug, separator, string_char, schema_name, rows):
    """
    Function that works in celery tasks loop and fills up CSV file
    On completion - changing DataSet status to 'Ready'
    """
    schema_columns = SchemaColumn.objects.filter(schema_name__schema_name=schema_name).order_by('column_order')
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=separator, quotechar=string_char, quoting=csv.QUOTE_ALL)

        column_names = ['number']
        column_names += [column.column_name for column in schema_columns]
        writer.writerow(column_names)

        for i in range(rows + 1):
            row = [i]
            for column in schema_columns:
                if column.column_type == 'Text':
                    data = ''.join(
                        random.choice(string.ascii_lowercase) for x in range(column.column_from, column.column_to))
                    row.append(data)
                elif column.column_type == 'Integer':
                    data = random.randint(column.column_from, column.column_to)
                    row.append(data)
                elif column.column_type == 'Date':
                    start_date = datetime.date(2020, 1, 1)
                    random_date = start_date + datetime.timedelta(days=random.randint(1, 1000))
                    row.append(random_date)
                else:
                    data_qs = FakeData.objects.filter(type=column.column_type)
                    row.append(random.choice(data_qs))
            writer.writerow(row)

        file.close()
    data_set = DataSet.objects.get(slug=slug)
    data_set.status = 'Ready'
    data_set.save()
    return file_path
