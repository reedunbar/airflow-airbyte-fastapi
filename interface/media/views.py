from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from django.shortcuts import render
import requests
from .models import ClientConnection, YouTubeConnection, YouTubeVideos, WordPressConnection, LLM, LLMConnection
import json


# Create a YouTube Data API client
api_key = 'AIzaSyAVBkiRKxpJQ53Gnu-boxCXKnhSbBFjlpE'
youtube = build('youtube', 'v3', developerKey=api_key)

def hello_world(request):
    return JsonResponse({'message': 'Hello, world!'})

def get_transcripts(request):
    if request.method == 'GET':
        video_id = request.GET.get('video_id')
        try:
            transcripts = YouTubeTranscriptApi.get_transcript(video_id)
            return JsonResponse({"video_id": video_id, "transcripts": transcripts})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=404)

def get_playlist_videos(request):
    if request.method == 'GET':
        playlist_id = request.GET.get('playlist_id')
        try:
            all_video_ids = get_playlist_items(playlist_id)
            return JsonResponse({"playlist_id": playlist_id, "video_ids": all_video_ids})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

# Helper method to retrieve playlist items
def get_playlist_items(playlist_id):
    video_ids = []
    next_page_token = None
    while True:
        playlist_response = youtube.playlistItems().list(
            part='status,contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        for item in playlist_response['items']:
            privacy_status = item['status']['privacyStatus']
            if privacy_status == 'public':
                video_ids.append(item['contentDetails']['videoId'])

        next_page_token = playlist_response.get('nextPageToken')
        if not next_page_token:
            break

    return video_ids

def get_client_connections(request):
    # connections = list(ClientConnection.objects.all().values())
    # return JsonResponse({'connections': connections})

    connections = list(ClientConnection.objects.all().values())
    for connection in connections:
        source_id = connection['source_id']
        if connection['connection_id'] == 1:  # Assuming 1 represents YouTubeConnection
            youtube_connection = YouTubeConnection.objects.values().get(id=source_id)
            source_info = {key: value for key, value in youtube_connection.items() if key != '_state'}
        elif connection['connection_id'] == 2:  # Assuming 2 represents WordPressConnection
            wordpress_connection = WordPressConnection.objects.get(id=source_id)
            source_info = {key: value for key, value in wordpress_connection.items() if key != '_state'}
        connection['source_info'] = source_info
        del connection['source_id']  # Remove source_id from response
    return JsonResponse({'connections': connections})

@csrf_exempt
def update_transcriptions(request):
    if request.method == 'POST':
        print('in post')
        playlist_id = request.POST.get('playlist_id')
        video_ids_transcribed = request.POST.getlist('video_ids_transcribed')

        try:
            for video_id_transcribed in video_ids_transcribed:
                # Check if video_id exists for the given playlist_id
                try:
                    youtube_video = YouTubeVideos.objects.get(playlist_id=playlist_id, video_id=video_id_transcribed)
                    youtube_video.transcribed = True  # Update transcribed status
                    youtube_video.save()
                except YouTubeVideos.DoesNotExist:
                    # Video_id does not exist, create a new entry
                    YouTubeVideos.objects.create(playlist_id=playlist_id, video_id=video_id_transcribed, transcribed=True)

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def step1_view(request):
    if request.method == 'POST':
        # Get selected ClientConnection ID from form submission
        connection_id = request.POST.get('connection_id')

        # Retrieve the selected ClientConnection from the database
        try:
            client_connection = ClientConnection.objects.get(id=connection_id)
        except ClientConnection.DoesNotExist:
            return JsonResponse({'error': 'ClientConnection not found'}, status=404)

        # Trigger the retrieval of video IDs (simulate for demo purposes)
        youtube_connection = YouTubeConnection.objects.get(id=client_connection.source_id)
        playlist_id = youtube_connection.playlist_id
        items = get_playlist_items(playlist_id)

        for video_id in items:
            # Create YouTubeVideos object for each video_id

            youtube_video, created = YouTubeVideos.objects.get_or_create(
                playlist_id=playlist_id,
                video_id=video_id,
                defaults={'transcribed': False}  # Set transcribed to False if object is newly created
            )
        
        response_data = {
            'message': 'Step 1 completed successfully',
            'redirect_url': '/admin/'  # Redirect to Step 2 upon success
        }

        return JsonResponse(response_data)

    connections = ClientConnection.objects.all()
    return render(request, 'media/trigger_dag.html', {'connections': connections})


def train_model(request):
    try:
        llms = LLM.objects.all()
        
        for llm in llms:
            llm_sources = LLMConnection.objects.filter(llm=llm)
            for source in llm_sources:
                payload = {
                    'bucket': source.bucket,
                    'llm_id': source.pk,
                    'source_id': source.client_connection_id,  # Assuming this is the correct field name
                    'metadata': source.metadata
                }
                
                # Vectorize LLM Source

        return JsonResponse({"payload": payload})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

