from django.urls import path
from django.shortcuts import render
from . import views

def test_layout_view(request):
    return render(request, 'test_layout.html')

urlpatterns = [
    path('login/', views.login_portal, name='login_portal'),
    path('', views.simple_chat_view, name='home'),
    path('test_layout/', test_layout_view, name='test_layout'),
    path('api/csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('api/upload/', views.upload_file, name='upload_file'),
    path('api/generation-status/', views.get_generation_status, name='get_generation_status'),
    path('api/user-latest-notes/', views.get_user_latest_notes, name='get_user_latest_notes'),
    path('api/notes-content/', views.get_notes_content, name='get_notes_content'),
    path('api/stream-notes/', views.stream_notes_content, name='stream_notes_content'),
    path('api/chat/', views.chat_message, name='chat_message'),
    path('api/questions/generate/', views.generate_questions, name='generate_questions'),
    path('api/questions/check-answer/', views.check_answer, name='check_answer'),
]