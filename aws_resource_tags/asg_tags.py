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
            'ResourceId': 'xxxxxxxx',
            'ResourceType': 'auto-scaling-group',
            'Key': 'ApplicationOwner',
            'Value': 'pkawale@tavisca.com',
            'PropagateAtLaunch': True
        },
        {
            'ResourceId': 'xxxxxxxx',
            'ResourceType': 'auto-scaling-group',
            'Key': 'ProductOwner',
            'Value': 'xxxxxxxx',
            'PropagateAtLaunch': True
        },
        {
            'ResourceId': 'xxxxxxxx',
            'ResourceType': 'auto-scaling-group',
            'Key': 'Purpose',
            'Value': 'Business',
            'PropagateAtLaunch': True
        },
        {
            'ResourceId': 'xxxxxxxx',
            'ResourceType': 'auto-scaling-group',
            'Key': 'Name',
            'Value': 'xxxxxxxx',
            'PropagateAtLaunch': True
        },
        {
            'ResourceId': 'xxxxxxxx',
            'ResourceType': 'auto-scaling-group',
            'Key': 'ApplicationRole',
            'Value': 'xxxxxxxx',
            'PropagateAtLaunch': True
        },
        {
            'ResourceId': 'xxxxxxxx',
            'ResourceType': 'auto-scaling-group',
            'Key': 'Environment',
            'Value': 'xxxxxxxx',
            'PropagateAtLaunch': True
        },
        {
            'ResourceId': 'xxxxxxxx',
            'ResourceType': 'auto-scaling-group',
            'Key': 'Product',
            'Value': 'xxxxxxxx',
            'PropagateAtLaunch': True
        }        
    ])
    print(response)


def main():
    asg_client = get_asg_client()
    add_asg_tags(asg_client)

if __name__ == "__main__":
    main()

