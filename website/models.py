from django.db import models
from django.contrib.auth.models import User




class Habit(models.Model):
	user = models.ForeignKey(User, on_delete = models.CASCADE)
	habit_name = models.CharField(max_length=100)
	frequency = models.CharField (max_length=10, choices=[('daily','Daily'),
														('Weekly','Weekly'),
														('Monthly','Monthly')])
	description = models.CharField(max_length=300, blank =True) 
	created_at = models.DateTimeField(auto_now_add = True)

	def __str__(self):
		return f"{self.habbit_name} - {self.user}"
	


class HabitLog(models.Model):
	habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="logs")
	date = models.DateField()
	completed =models.BooleanField(default = True)


	def __str__(self):
		return f"{self.habit.habit_name} - {self.date} - {self.completed}"
