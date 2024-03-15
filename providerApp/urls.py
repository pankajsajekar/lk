from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.SearchDCView.as_view()),
    path('DCView/', views.DCView.as_view()),
]
