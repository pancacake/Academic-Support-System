from django.urls import path
from . import views

app_name = 'questions'

urlpatterns = [
    path('', views.questions_page, name='questions_page'),
    path('generate-structured/', views.generate_structured_questions, name='generate_structured'),
    path('submit-answer/', views.submit_answer, name='submit_answer'),
    path('generate-report/', views.generate_answer_report, name='generate_answer_report'),
]
