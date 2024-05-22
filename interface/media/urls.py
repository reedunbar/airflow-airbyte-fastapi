from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello_world, name='hello_world'),
    path('videos/', views.get_playlist_videos, name='get_playlist_videos'),
    path('transcript/', views.get_transcripts, name='get_transcripts'),
    path('connections/', views.get_client_connections, name='get_client_connections'),
    path('trigger-dag/', views.step1_view, name='trigger_airflow_dag'),
    path('update_transcriptions/', views.update_transcriptions, name='update_transcriptions'),
    path('train/', views.train_model, name='train')
]