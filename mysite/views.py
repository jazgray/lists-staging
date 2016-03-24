'''
Created on Feb 13, 2016

@author: Jim
'''
from django.http import HttpResponse
def home(request):
  response = 'Yay! It works!!'
  return HttpResponse(response)