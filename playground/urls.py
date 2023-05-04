from django.urls import path
from . import views

urlpatterns = [
    path('findActors/', views.getActors),
    path('result/', views.result, name='result'),

]
