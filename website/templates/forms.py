from django.contrib.auth.models import User
from django import forms
from .models import Habit, Habitlog


class AddHabitForm(forms.ModelForm):
	
	habit_name = forms.CharField(required = True, widget = forms.widgets.TextInput(attrs={"placeholder":"Habit","class":"form-control"}),label="")
	frequency = forms.ChoiceField(required = True,
								  choices=[('daily','Daily'),
										  ('Weekly','Weekly'),
										  ('Monthly','Monthly')],	
								  widget = forms.Select(attrs={"class":"form-control"}))
	
	description = forms.CharField(required = False, widget = forms.widgets.TextInput(attrs={"placeholder":"Description","class":"form-control"}),label="")


	class Meta:
		model = Habit
		fields =('habit_name','frequency','description')














