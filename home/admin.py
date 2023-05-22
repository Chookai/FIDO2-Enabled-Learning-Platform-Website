from django.contrib import admin

# Register your models here.



from django import forms
from phonenumber_field.widgets import PhoneNumberPrefixWidget

from .models import AI_Coursework

admin.site.register(AI_Coursework)