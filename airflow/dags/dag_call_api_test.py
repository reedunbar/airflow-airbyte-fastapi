from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import requests

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

def check_api():
    response = requests.get("http://interface:8081/api/connections/")
    response.raise_for_status()
    return response.status_code == 200

with DAG('call_api_dag', default_args=default_args, schedule_interval='@daily') as dag:
    
    api_sensor = PythonOperator(
        task_id='api_sensor',
        python_callable=check_api,
    )

    api_sensor
