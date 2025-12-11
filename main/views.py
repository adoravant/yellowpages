
import os
from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
from .models import Lead, Dato
from django.http import HttpResponse
from django.conf import settings
from utils import *
import csv
# main/views.py
import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def home(request):
	"""donation page no ++ download"""
	leads = Lead.objects.filter(country="CANADA").exclude(website="NOWEB").exclude(website_status=None).exclude(website_type="FACEBOOK").filter(website_status="DOWNSSL")
	template = "main/index.html"
	return render(request, template, context = {"leads" : leads})





def refresh(request):
	"""donation page no ++ download"""
	leads = Lead.objects.filter(country="CANADA").exclude(website="NOWEB").exclude(website_status=None).exclude(website_type="FACEBOOK").filter(website_status__endswith="NOSSL")
	template = "main/index_list.html"
	return render(request, template, context = {"leads" : leads})


def export(request):
    response = HttpResponse(content_type='text/csv')

    writer = csv.writer(response)
    writer.writerow(['Name', 'phone', 'phone_type', 'country', "city"])

    for lead in Dato.objects.all().values_list('name', 'phone', 'phone_type', 'country', 'city'):
        writer.writerow(lead)

    response['Content-Disposition'] = 'attachment; filename="Lead.csv"'

    return response



import subprocess
import os
DEVICE_ID = "5eba6c4010bc490b953192877e48e263"

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def call_phone(request):
    number = request.GET.get("number") or request.POST.get("number")
    if not number:
        return JsonResponse({"error": "No number provided"}, status=400)

    try:
        r = requests.post("http://localhost:5000/call", json={"phone": number})
        return JsonResponse(r.json())
    except requests.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)



