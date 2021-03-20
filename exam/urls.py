from django.urls import path

from . import views

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('instructions', views.instructions, name='instructions'),
    path('take-exam', views.take_exam, name='take_exam' ),
    path('finished-exam', views.finished_exam, name='finished_exam'),
]