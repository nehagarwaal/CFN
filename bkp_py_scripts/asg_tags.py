import requests
import boto3
import sys
import os
import json


def get_asg_client():
    client = boto3.client("autoscaling")
    return client

def add_asg_tags(asg_client):
    response = asg_client.create_or_update_tags(
    Tags=[
        {
            'ResourceId': 'Flights-RabbitMQ-SSL',
            'ResourceType': 'auto-scaling-group',
            'Key': 'ApplicationOwner',
            'Value': 'pkawale@tavisca.com',
            'PropagateAtLaunch': True
        },
        {
            'ResourceId': 'Flights-RabbitMQ-SSL',
            'ResourceType': 'auto-scaling-group',
            'Key': 'ProductOwner',
            'Value': 'pkawale@tavisca.com',
            'PropagateAtLaunch': True
        },
        {
            'ResourceId': 'Flights-RabbitMQ-SSL',
            'ResourceType': 'auto-scaling-group',
            'Key': 'Purpose',
            'Value': 'Business',
            'PropagateAtLaunch': True
        },
        {
            'ResourceId': 'Flights-RabbitMQ-SSL',
            'ResourceType': 'auto-scaling-group',
            'Key': 'Name',
            'Value': 'Flights-RabbitMQ-SSL',
            'PropagateAtLaunch': True
        },
        {
            'ResourceId': 'Flights-RabbitMQ-SSL',
            'ResourceType': 'auto-scaling-group',
            'Key': 'ApplicationRole',
            'Value': 'RMQ',
            'PropagateAtLaunch': True
        },
        {
            'ResourceId': 'Flights-RabbitMQ-SSL',
            'ResourceType': 'auto-scaling-group',
            'Key': 'Environment',
            'Value': 'travel-stage',
            'PropagateAtLaunch': True
        },
        {
            'ResourceId': 'Flights-RabbitMQ-SSL',
            'ResourceType': 'auto-scaling-group',
            'Key': 'Product',
            'Value': 'Flights',
            'PropagateAtLaunch': True
        }        
    ])
    print(response)


def main():
    asg_client = get_asg_client()
    add_asg_tags(asg_client)

if __name__ == "__main__":
    main()

