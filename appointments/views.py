from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def my_appointments(request):
    return render(request, 'appointments/my_appointments.html')


@login_required
def appointment_history(request):
    return render(request, 'appointments/appointment_history.html')


@login_required
def review_history(request):
    return render(request, 'appointments/review_history.html')
