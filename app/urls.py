from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('available_slots/', views.available_slots, name='available_slots'),
    path('reserve_slot/', views.reserve_slot, name='reserve_slot'),
]