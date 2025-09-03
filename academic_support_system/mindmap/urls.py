from django.urls import path
from . import views

urlpatterns = [
    path('mindmap/', views.mindmap_view, name='mindmap'),
    path('mindmap/<int:note_id>/', views.mindmap_view, name='mindmap_with_id'),
    path('api/mindmap/latest-notes/', views.get_latest_notes, name='get_latest_notes'),
    path('api/mindmap/parse/', views.parse_notes_to_mindmap, name='parse_notes_to_mindmap'),
    path('api/mindmap/update-node/', views.update_mindmap_node, name='update_mindmap_node'),
    path('api/mindmap/generate-section/', views.generate_mindmap_section, name='generate_mindmap_section'),
]
