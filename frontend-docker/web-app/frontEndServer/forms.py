from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Package, Product, Warehouse, my_user
from django.views.generic.edit import FormView
from django.utils import timezone
import datetime


class UserRegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = my_user
        fields = [
            'email',
            'username',
        ]
