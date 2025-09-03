from django.urls import path
from . import views
from django.http import HttpResponse
from django.shortcuts import render

# 添加一个简单的测试视图来验证URL路由
def test_export_view(request):
    return HttpResponse("Export URL is working! This is a test.")

def test_fetch_stream_view(request):
    """测试页面视图"""
    with open('test_fetch_stream.html', 'r', encoding='utf-8') as f:
        content = f.read()
    return HttpResponse(content, content_type='text/html')

def simple_stream_test_view(request):
    """简单流式测试页面"""
    with open('simple_stream_test.html', 'r', encoding='utf-8') as f:
        content = f.read()
    return HttpResponse(content, content_type='text/html')

def test_image_paths_view(request):
    """图片路径测试页面"""
    with open('test_image_paths.html', 'r', encoding='utf-8') as f:
        content = f.read()
    return HttpResponse(content, content_type='text/html')

def debug_notes_display_view(request):
    """笔记显示调试页面"""
    with open('debug_notes_display.html', 'r', encoding='utf-8') as f:
        content = f.read()
    return HttpResponse(content, content_type='text/html')

urlpatterns = [
    path('api/notes/start/', views.start_note_generation, name='start_note_generation'),
    path('api/notes/status/', views.get_note_generation_status, name='get_note_generation_status'),
    path('api/notes/stream/', views.stream_notes_content, name='stream_notes_content'),
    path('api/notes/simple-stream/', views.simple_stream_test, name='simple_stream_test'),
    path('api/notes/ai-chat/', views.ai_chat_with_notes, name='ai_chat_with_notes'),
    path('api/notes/export/', views.export_notes, name='export_notes'),
    path('api/notes/export-test/', test_export_view, name='test_export'),
    path('api/notes/sections/', views.get_note_sections, name='get_note_sections'),
    path('test_fetch_stream.html', test_fetch_stream_view, name='test_fetch_stream'),
    path('simple_stream_test.html', simple_stream_test_view, name='simple_stream_test_page'),
    path('test_image_paths.html', test_image_paths_view, name='test_image_paths'),
    path('debug_notes_display.html', debug_notes_display_view, name='debug_notes_display'),
]
