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
node_metric_list = str(os.environ["metrics_list"]).split(",")

def get_cloudwatch_client():
    client = boto3.client("cloudwatch")
    return client

def get_node_metrics(route):
    cloudwatch_put_data = []
    node_details = make_api_request(route)
    for node in node_details:
        node_name = node.get("name")
        for node_metric_name in node_metric_list:
            data = get_metric_data_structure(node_metric_name, node.get(node_metric_name), node_name)
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

def get_metric_data_structure(name,value,node_name):
    data = {
        "MetricName" : name,
        "Value":value,
        "Unit": "Count",
        "Dimensions": [
                {
                    "Name": "node",
                    "Value": node_name
                },
            ]
    }
    return data

def put_metrics_to_cloudwatch(cw_client,cloudwatch_data):
    try:
        for data in cloudwatch_data:
            cw_client.put_metric_data(
                Namespace = "RabbitMQ_Flights_Nodes",
                MetricData=[data]
            )
    except:
        print(sys.exc_info)
        pass

def lambda_handler(event, context):
    cw_client = get_cloudwatch_client()
    node_metric_dictionary = get_node_metrics("/api/nodes")
    put_metrics_to_cloudwatch(cw_client,node_metric_dictionary)