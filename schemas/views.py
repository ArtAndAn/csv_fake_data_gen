from django.shortcuts import render


def data_schemas(request):
    return render(request, 'schemas/schemas.html')


def new_schema(request):
    return render(request, 'schemas/new_schema.html')


def data_sets(request):
    return render(request, 'schemas/data_sets.html')
