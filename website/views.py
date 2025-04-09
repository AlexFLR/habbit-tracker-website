from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages


def home(request):

	return render(request,'home.html',{})


def login(request):

	return render(request,'login.html',{})



def logout_user(request):
	logout(request)
	messages.success(request, "You have been logged out.")
	return redirect('home')




def habits(request):

	return render(request,'habits.html',{})



def analytics(request):

	return render(request,'analytics.html',{})