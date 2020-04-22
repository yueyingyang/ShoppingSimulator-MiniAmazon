from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Package, Product, Warehouse
from django.views.generic.edit import FormView
from django.utils import timezone
import datetime
from flatpickr import DateTimePickerInput

class queryStatus(forms.Form):
    upsAccount = forms.CharField(max_length=150, label="upsAccount")
    pkgid = forms.CharField(max_length=150, label="Package ID")

