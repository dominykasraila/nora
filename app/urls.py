from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('events/', views.google_calendar_events, name='events'),
    path('create_event/', views.create_event, name='create_event'),
]