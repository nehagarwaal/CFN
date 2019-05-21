import requests
from requests.auth import HTTPBasicAuth
import boto3
import sys
import os
import json

rabbitmq_endpoint = str(os.environ["rabbitmq_endpoint"])
rabbitmq_username = str(os.environ["rabbitmq_username"])
rabbitmq_password = str(os.environ["rabbitmq_password"])
rabbitmq_port = str(os.environ["rabbitmq_port"])
queue_metric_list = str(os.environ["metrics_list"]).split(",")

def make_api_request(route):
    try:
        url = "{}{}".format(rabbitmq_endpoint+":"+rabbitmq_port,route)
        response = requests.get(url,auth=(rabbitmq_username,rabbitmq_password))
        response_data = json.loads(response.text)
        return response_data
    except Exception as e:
        print(str(e))

def get_cloudwatch_client():
    client = boto3.client("cloudwatch")
    return client

def get_metric_data_structure(name,value,queue_name):
    data = {
        "MetricName" : name,
        "Value":value,
        "Unit": "Count",
        "Dimensions": [
                {
                    "Name": "Queue",
                    "Value": queue_name
                },
            ]
    }
    return data

def get_queue_metrics(route):
    cloudwatch_put_data = []
    queue_details = make_api_request(route)
    try:
        for queue in queue_details:
            queue_name = queue.get("name")
            if "dlq" not in queue_name:
                for queue_metric_name in queue_metric_list:
                    data = get_metric_data_structure(queue_metric_name,queue.get(queue_metric_name),queue_name)
                    print(data)
                    cloudwatch_put_data.append(data)
            elif "dlq" in queue_name:
                data = get_metric_data_structure("messages",queue.get("messages"),queue_name)
                cloudwatch_put_data.append(data)
        return cloudwatch_put_data
    except Exception as e:
        print(str(e))
        pass


def put_metrics_to_cloudwatch(cw_client,cloudwatch_data):
    try:
        for data in cloudwatch_data:
            cw_client.put_metric_data(
                Namespace = "RabbitMQ_Flights",
                MetricData=[data]
            )
    except:
        print(sys.exc_info)
        pass

def lambda_handler(event, context):
    cw_client = get_cloudwatch_client()
    queue_metric_dictionary = get_queue_metrics("/api/queues/")
    put_metrics_to_cloudwatch(cw_client,queue_metric_dictionary)