import re
from django.shortcuts import render


def home(request):
    return render(request,'ecom/base.html')