from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('google_calendar_events/', views.google_calendar_events, name='google_calendar_events'),
]