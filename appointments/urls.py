from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.my_appointments, name='my_appointments'),
    path('my/', views.my_appointments, name='my_appointments'),
    path('history/', views.appointment_history, name='appointment_history'),
    path('reviews/', views.review_history, name='review_history'),
]
