from django.shortcuts import render


def data_schemas(request):
    return render(request, 'schemas/schemas.html')
