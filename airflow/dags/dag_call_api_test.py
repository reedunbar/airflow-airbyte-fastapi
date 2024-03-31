from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.utils.dates import days_ago
from operators.HttpCustom import HttpToGCSBucketOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG('call_api_dag', default_args=default_args, schedule_interval='@daily') as dag:
    
    # Define a task to wait for the API to be available
    api_sensor = HttpSensor(
        task_id='api_sensor',
        http_conn_id='',  # Connection ID for the API endpoint
        method='HEAD',
        endpoint='http://webapp:8081',  # Endpoint to check if API is healthy
        response_check=lambda response: True if response.status_code == 200 else False,
        poke_interval=30,
        timeout=600,
        mode='reschedule',
        dag=dag,
    )

    # Define a task to upload JSON data to GCS bucket
    upload_to_gcs_task = HttpToGCSBucketOperator(
        task_id='upload_to_gcs_task',
        api_url='http://localhost:8081/test1',  # Connection ID for GCP
        headers={"Content-Type": "application/json"},
        gcs_bucket='airflow-airbyte-fastapi',  # Name of your GCS bucket
        gcs_object_name='data.json',  # Name of the file to be uploaded to GCS
        dag=dag,
    )

    api_sensor >> upload_to_gcs_task