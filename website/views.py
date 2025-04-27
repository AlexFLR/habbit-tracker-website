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
from calendar import monthrange
from django.urls import reverse
import os
from django.conf import settings
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from django.http import HttpResponse
import base64
import plotly.express as px

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

    # Toate obiceiurile utilizatorului (fără filtru)
    all_habits = list(Habit.objects.filter(user=request.user))

    # HabitFilter aplicat separat
    habit_filter = HabitFilter(request.GET, queryset=Habit.objects.filter(user=request.user))
    filtered_habits = habit_filter.qs

    # Ultimele 7 zile
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]

    visible_habits = []
    completion_status = {}
    history = {}

    for habit in all_habits:
        # Istoric pe 7 zile
        history[habit.id] = {}
        for day in last_7_days:
            log = HabitLog.objects.filter(habit=habit, date=day, completed=True).first()
            history[habit.id][day] = True if log else False

        # Determinăm dacă habit-ul ar trebui să apară în secțiunea „Your habits”
        show = True
        last_log = HabitLog.objects.filter(habit=habit, completed=True).order_by('-date').first()

        if habit.frequency == 'weekly' and last_log:
            if last_log.date.isocalendar()[1] == today.isocalendar()[1] and last_log.date.year == today.year:
                show = False
        elif habit.frequency == 'monthly' and last_log:
            if last_log.date.month == today.month and last_log.date.year == today.year:
                show = False

        if show:
            visible_habits.append(habit)
            completed_today = HabitLog.objects.filter(habit=habit, date=today, completed=True).first()
            completion_status[habit.id] = True if completed_today else False

    context = {
        'habits': visible_habits,
        'all_habits': all_habits,              # pentru heatmap
        'filtered_habits': filtered_habits,    # pentru tabelul filtrabil
        'filter': habit_filter,
        'completion_status': completion_status,
        'last_7_days': last_7_days,
        'history': history,
        'today': today,
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

    log, created = HabitLog.objects.get_or_create(
        habit=habit,
        date=today,
        defaults={'completed': True}
    )

    if not created:
        log.completed = not log.completed
        log.save()

    # 🔥 Redirect curat, fără GET parameters
    return redirect(reverse('habits'))




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

    
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None

    chart_data = {}

    if start_date and end_date:
        if selected_habit_id:
            selected_habit = get_object_or_404(Habit, id=selected_habit_id, user=request.user)
            logs = HabitLog.objects.filter(
                habit=selected_habit,
                date__range=[start_date, end_date]
            ).values('date').annotate(completed_count=Count('id')).order_by('date')
        else:
            logs = HabitLog.objects.filter(
                habit__user=request.user,
                date__range=[start_date, end_date]
            ).values('date').annotate(completed_count=Count('id')).order_by('date')

        chart_data = {
            'labels': [log['date'].strftime('%Y-%m-%d') for log in logs],
            'data': [log['completed_count'] for log in logs],
        }

    
    today = date.today()
    first_day = date(today.year, 1, 1)  
    last_day = date(today.year, 12, 31)  


    if selected_habit_id:
        selected_habit = get_object_or_404(Habit, id=selected_habit_id, user=request.user)
        heatmap_logs = HabitLog.objects.filter(
            habit=selected_habit,
            date__range=[first_day, last_day],
            completed=True
        ).values('date').annotate(count=Count('id'))
    else:
        heatmap_logs = HabitLog.objects.filter(
            habit__user=request.user,
            date__range=[first_day, last_day],
            completed=True
        ).values('date').annotate(count=Count('id'))

    heatmap_data = {
        log['date'].strftime('%Y-%m-%d'): log['count'] for log in heatmap_logs
    }

    
    calendar_weeks = []
    start = first_day - timedelta(days=first_day.weekday())  
    end = last_day
    current = start

    while current <= end:
        week = []
        for _ in range(7):
            week.append(current)
            current += timedelta(days=1)
        calendar_weeks.append(week)

    context = {
        'habits': habits,
        'selected_habit_id': selected_habit_id,
        'chart_type': chart_type,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'chart_data': json.dumps(chart_data),
        'today': today,
        'calendar_weeks': calendar_weeks,
        'heatmap_data': heatmap_data,
    }

    return render(request, 'analytics.html', context)




@login_required
def dataexplorer_select_view(request):
    df_json = request.session.get('dataexplorer_df')

    if not df_json:
        return redirect('dataexplorer_upload')

    df = pd.read_json(df_json)
    columns = df.columns.tolist()

    if request.method == 'POST':
        chart_type = request.POST.get('chart_type')

        if chart_type == 'scatter':
            column_x = request.POST.get('column_x')
            column_y = request.POST.get('column_y')
            request.session['dataexplorer_options'] = {
                'chart_type': chart_type,
                'column_x': column_x,
                'column_y': column_y,
            }
        else:
            column = request.POST.get('column')
            bins = request.POST.get('bins') or 10
            request.session['dataexplorer_options'] = {
                'chart_type': chart_type,
                'column': column,
                'bins': bins,
            }

        return redirect('dataexplorer_graph')

    return render(request, 'dataexplorer/select.html', {'columns': columns})

def dataexplorer_upload_view(request):
    if request.method == 'POST':
        file = request.FILES['file']

        # Salvăm temporar fișierul
        file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', file.name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Citim fișierul cu pandas
        df = pd.read_csv(file_path, sep=';')

        # Salvăm dataframe-ul în sesiune ca JSON
        request.session['dataexplorer_df'] = df.to_json()

        return redirect('dataexplorer_select')

    return render(request, 'dataexplorer/upload.html')



@login_required
def dataexplorer_graph_view(request):
    df_json = request.session.get('dataexplorer_df')
    options = request.session.get('dataexplorer_options')

    if not df_json or not options:
        return redirect('dataexplorer_upload')

    df = pd.read_json(df_json)
    chart_type = options.get('chart_type')

    fig = None

    if chart_type == 'histogram':
        column = options.get('column')
        bins = int(options.get('bins', 10))
        fig = px.histogram(df, x=column, nbins=bins, title=f"Histogram for {column}")

    elif chart_type == 'scatter':
        column_x = options.get('column_x')
        column_y = options.get('column_y')
        fig = px.scatter(df, x=column_x, y=column_y, title=f"Scatter plot: {column_x} vs {column_y}")

    elif chart_type == 'line':
        column_x = options.get('column_x')
        column_y = options.get('column_y')
        fig = px.line(df, x=column_x, y=column_y, title=f"Line plot: {column_x} vs {column_y}")

    elif chart_type == 'box':
        column = options.get('column')
        fig = px.box(df, y=column, title=f"Box plot for {column}")

    if not fig:
        return HttpResponse("Invalid graphic.")

    graph_html = fig.to_html(full_html=False, default_height=600)

    return render(request, 'dataexplorer/graph.html', {'graph': graph_html})




def dataexplorer_download_view(request):
    df_json = request.session.get('dataexplorer_df')
    options = request.session.get('dataexplorer_options')

    if not df_json or not options:
        return redirect('dataexplorer_select')

    df = pd.read_json(df_json)

    fig, ax = plt.subplots(figsize=(8, 5))

    chart_type = options.get('chart_type')

    if chart_type == 'histogram':
        column = options.get('column')
        bins = options.get('bins')
        bins = int(bins) if bins else 10
        df[column].hist(bins=bins, ax=ax)
        ax.set_title(f'Histogram for {column}')

    elif chart_type == 'scatter':
        column_x = options.get('column_x')
        column_y = options.get('column_y')
        df.plot.scatter(x=column_x, y=column_y, ax=ax)
        ax.set_title(f'Scatter plot {column_x} vs {column_y}')

    elif chart_type == 'boxplot':
        column = options.get('column')
        df.boxplot(column=column, ax=ax)
        ax.set_title(f'Boxplot for {column}')

    
    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    
    response = HttpResponse(buffer, content_type='image/png')
    response['Content-Disposition'] = 'attachment; filename="grafic.png"'
    return response


































