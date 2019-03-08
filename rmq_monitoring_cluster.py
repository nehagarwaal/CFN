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
cluster_metric_list = str(os.environ["metrics_list"]).split(",")

def get_cloudwatch_client():
    client = boto3.client("cloudwatch")
    return client

def get_cluster_metrics(route):
    cloudwatch_put_data = []
    cluster_details = make_api_request(route)
    cluster_name = cluster_details.get("cluster_name")
    for cluster_metric_name in cluster_metric_list:
        if '.' in cluster_metric_name:
            metric_name = cluster_metric_name.split('.', 3)
            metric_value = cluster_details.get(metric_name[0]).get(metric_name[1])
            data = get_metric_data_structure(cluster_metric_name, metric_value, cluster_name)
        else:
            data = get_metric_data_structure(cluster_metric_name, cluster_details.get(cluster_metric_name), cluster_name)
        cloudwatch_put_data.append(data)
    return cloudwatch_put_data
        
def make_api_request(route):
    try:
        url = "{}{}".format(rabbitmq_endpoint+":"+rabbitmq_port,route)
        print(url)
        response = requests.get(url,auth=(rabbitmq_username,rabbitmq_password))
        response_data = json.loads(response.text)
        return response_data
    except Exception as e:
        print(str(e))

def get_metric_data_structure(name,value,cluster_name):
    data = {
        "MetricName" : name,
        "Value":value,
        "Unit": "Count",
        "Dimensions": [
                {
                    "Name": "cluster",
                    "Value": cluster_name
                },
            ]
    }
    return data

def put_metrics_to_cloudwatch(cw_client,cloudwatch_data):
    try:
        for data in cloudwatch_data:
            cw_client.put_metric_data(
                Namespace = "RabbitMQ_Flights_Cluster",
                MetricData=[data]
            )
    except:
        print(sys.exc_info)
        pass

def lambda_handler(event, context):
    cw_client = get_cloudwatch_client()
    cluster_metric_dictionary = get_cluster_metrics("/api/overview")
    put_metrics_to_cloudwatch(cw_client,cluster_metric_dictionary)