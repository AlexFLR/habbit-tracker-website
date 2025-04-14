from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from .models import Habit, HabitLog
from datetime import date, timedelta
from .forms import AddHabitForm
from .filters import HabitFilter
from django.utils.timezone import now
from django.utils.dateparse import parse_date
from django.db.models import Count
import json


def home(request):

	return render(request,'home.html',{})


def login(request):

	return render(request,'login.html',{})


def logout_user(request):
	logout(request)
	messages.success(request, "You have been logged out.")
	return redirect('home')


@login_required
def habits(request):
    today = date.today()
    user_habits = Habit.objects.filter(user=request.user)
    habit_filter = HabitFilter(request.GET, queryset=user_habits)
    all_habits = habit_filter.qs

    # ⏳ ultimele 7 zile
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]  # de la Luni până azi

    visible_habits = []
    completion_status = {}
    history = {}

    for habit in all_habits:
        # istoric pt acest habit pe ultimele 7 zile
        history[habit.id] = {}

        for day in last_7_days:
            log = HabitLog.objects.filter(habit=habit, date=day, completed=True).first()
            history[habit.id][day] = True if log else False

        last_log = HabitLog.objects.filter(habit=habit, completed=True).order_by('-date').first()
        show = True

        if habit.frequency == 'weekly' and last_log:
            if last_log.date.isocalendar()[1] == today.isocalendar()[1] and last_log.date.year == today.year:
                show = False
        elif habit.frequency == 'monthly' and last_log:
            if last_log.date.month == today.month and last_log.date.year == today.year:
                show = False

        if show:
            visible_habits.append(habit)
            log = HabitLog.objects.filter(habit=habit, date=today, completed=True).first()
            completion_status[habit.id] = True if log else False

    context = {
        'habits': visible_habits,
        'all_habits': all_habits,
        'today': today,
        'filter': habit_filter,
        'completion_status': completion_status,
        'last_7_days': last_7_days,
        'history': history,
    }

    return render(request, 'habits.html', context)




def add_record(request):
	form = AddHabitForm(request.POST or None)
	if request.user.is_authenticated:
		if request.method =="POST":
			if form.is_valid():
				add_record = form.save(commit = False)
				add_record.user = request.user
				add_record.save()
				messages.success(request,"Record Added")
				return redirect("habits")
		return render(request,'add_record.html',{'form':form});
	else:
		messages.success(request,"You are not authenticated. U must be logged in!")
		return redirect("login")


@login_required
def edit_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id)
    if request.method == 'POST':
        habit.habit_name = request.POST.get('name')
        habit.frequency = request.POST.get('frequency')
        habit.description = request.POST.get('description')
        habit.save()
        return redirect('habits')
    return render(request, 'edit_habit.html', {'habit': habit})


def toggle_habit_completion(request, habit_id):
	habit = get_object_or_404(Habit, id=habit_id, user=request.user)
	today = date.today()

	log, created = HabitLog.get_or_create(
		habit= habit,
		date=today,
		defaults={'completed':True})

	if not created:
		log.completed = not log.completed
		log.save()
	return redirect('habits')

@login_required
def delete_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id)
    if request.method == 'POST':
        habit.delete()
        return redirect('habits')  
    return redirect('habits')






@login_required
def analytics(request):
    habits = Habit.objects.filter(user=request.user)
    selected_habit_id = request.GET.get('habit')
    chart_type = request.GET.get('chart', 'bar')

    # date parsing
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None

    chart_data = {}

    if start_date and end_date:
        if selected_habit_id:
            # grafic pentru un singur habit
            selected_habit = get_object_or_404(Habit, id=selected_habit_id, user=request.user)
            logs = (
                HabitLog.objects
                .filter(habit=selected_habit, date__range=[start_date, end_date])
                .values('date')
                .annotate(completed_count=Count('id'))
                .order_by('date')
            )
        else:
            # ✅ grafic combinat pentru toate habit-urile
            logs = (
                HabitLog.objects
                .filter(habit__user=request.user, date__range=[start_date, end_date])
                .values('date')
                .annotate(completed_count=Count('id'))
                .order_by('date')
            )

        chart_data = {
            'labels': [log['date'].strftime('%Y-%m-%d') for log in logs],
            'data': [log['completed_count'] for log in logs],
        }

    context = {
        'habits': habits,
        'chart_type': chart_type,
        'selected_habit_id': selected_habit_id,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'analytics.html', context)







