from django import forms

from .models import Logger

class LogForm(forms.ModelForm):
    class Meta:
        model = Logger
        fields = ['first_name', 'last_name', 'email', 'skills', 'workexp']

class filterForm(forms.Form):
    country = forms.CharField(max_length=50)
    salary = forms.IntegerField(max_value=1000000)