from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from datetime import datetime, timedelta
import requests
import json

# Define the default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 5, 4),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
}

# Create the DAG object
dag = DAG(
    'youtube_transcript_to_gcs',
    default_args=default_args,
    description='Retrieve YouTube video transcripts and push to GCS',
    schedule_interval='@daily',  # Run daily
)

def get_client_connections_from_app():
    api_url = f'http://interface:8081/api/connections/'
    response = requests.get(api_url)
    response.raise_for_status()
    connections = response.json()['connections']
    return connections

# Define a function to retrieve all video IDs from a playlist using an API
def get_video_ids_from_playlist(playlist_id):
    api_url = f'http://interface:8081/api/videos?playlist_id={playlist_id}'
    response = requests.get(api_url)
    response.raise_for_status()  # Raise exception for non-2xx responses
    video_ids = response.json()['video_ids']
    return video_ids

# Define a function to get transcript for a video ID using an API
def update_transcription_status(playlist_id, video_ids):
    payload = {
        'playlist_id': playlist_id,
        'video_ids_transcribed': video_ids
    }
    response = requests.post(url="http://interface:8081/api/update_transcriptions/", data=payload)
    response.raise_for_status()  # Raise exception for non-2xx responses
    return response.status_code == 200


# Define a function to get transcript for a video ID using an API
def get_video_transcript(video_id):
    api_url = f'http://interface:8081/api/transcript?video_id={video_id}'
    response = requests.get(api_url)
    response.raise_for_status()  # Raise exception for non-2xx responses
    transcript = response.json()
    return transcript


def convert_json_to_text(data):
    text = ' '.join(transcript['text'] for transcript in data['transcripts'])
    return text


# Define a function to push transcript data to GCS
def upload_to_gcs(data, bucket_name, object_name):
    gcs_hook = GCSHook(gcp_conn_id="google_conn")
    gcs_hook.upload(
        bucket_name=bucket_name, 
        object_name=object_name, 
        data=data, 
        mime_type='text/plain'
    )

# Define the main task function to orchestrate the workflow
def process_playlist_videos(bucket_name):
    connections = get_client_connections_from_app()
    for connection in connections:
        playlist_id = connection['source_info']['playlist_id']
        video_ids = get_video_ids_from_playlist(playlist_id)
        for video_id in video_ids:
            transcript_as_json = get_video_transcript(video_id)
            #json_object_name = f'{playlist_id}/{video_id}.json'
            #upload_to_gcs(transcript_as_json, bucket_name, json_object_name)
            transcript_as_text = convert_json_to_text(transcript_as_json)
            text_object_name = f'{playlist_id}/cleaned/{video_id}.txt'
            upload_to_gcs(transcript_as_text, bucket_name, text_object_name)
            update_transcription_status(playlist_id, list(video_id))


# Define the DAG tasks
with dag:
    # Task to process playlist videos
    process_videos_task = PythonOperator(
        task_id='process_playlist_videos',
        python_callable=process_playlist_videos,
        op_kwargs={'bucket_name': 'airflow-airbyte-fastapi'},
    )

    # Set task dependencies
    process_videos_task