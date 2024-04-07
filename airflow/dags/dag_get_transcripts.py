import requests
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.providers.http.sensors.http import HttpSensor
from airflow.operators.dummy import DummyOperator
import json


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 4, 7),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def fetch_api_data(video_id: str = "YOUR_VIDEO_ID_HERE"):
    # Replace the URL with your actual endpoint that triggers the transcript process
    response = requests.get(f"http://webapp:8081/transcripts?video_id={video_id}")
    response.raise_for_status()
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError("Failed to get transcript")



def upload_to_gcs(data, bucket_name, object_name):
    gcs_hook = GCSHook(gcp_conn_id="google_conn")
    gcs_hook.upload(bucket_name=bucket_name, object_name=object_name, data=json.dumps(data), mime_type='application/json')


def fetch_and_upload():
    data = fetch_api_data('pOL59k9AQeo')
    upload_to_gcs(data, "airflow-airbyte-fastapi", "data/transcript.json")

with DAG('api_to_gcs', default_args=default_args, schedule_interval='@daily') as dag:

    start = DummyOperator(task_id='start')

    # Check if the API is running
    check_api_health = HttpSensor(
        task_id='check_api_health',
        http_conn_id='fastapi_webapp',  # Make sure to set this connection in Airflow
        endpoint='/',  # Adjust if you have a specific health check endpoint
        method='GET',
        response_check=lambda response: response.status_code == 200,
        poke_interval=5,
        timeout=20,
    )

    fetch_upload_task = PythonOperator(
        task_id='fetch_and_upload_task',
        python_callable=fetch_and_upload,
    )

    start >> check_api_health >> fetch_upload_task
