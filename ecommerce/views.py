from django.shortcuts import render
from ecommerce.models import *
from django.http.response import HttpResponse
import pandas as pd

# Create your views here.
def getHompage(request):
    result  = Furniture.objects.all()

    return render(request,'homepage.html', {'furniture':result})

def goCatalog(request): 
    return render(request,'catalog.html')

def goDonate(request):
    return render(request,'donate.html')

def goAbout(request):
    return render(request,'about.html')

def getAllRecomemdation(request):
    furniture_df = pd.DataFrame(list(Furniture.objects.all.values()))



