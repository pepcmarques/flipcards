from django.http import HttpResponse  # noqa
from django.shortcuts import render


def index(request):
    return render(request, 'base.html')
