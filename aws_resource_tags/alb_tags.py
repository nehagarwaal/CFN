import requests
import boto3
import sys
import os
import json


def get_alb_client():
    client = boto3.client("elbv2")
    return client

def add_alb_tags(alb_client):
    response = alb_client.add_tags(
    ResourceArns=[
        'arn:aws:xxxxxxxx',
    ],
    Tags=[
        {
            'Key': 'ApplicationOwner',
            'Value': 'xxxxxxxx'
        },
        {
            'Key': 'ProductOwner',
            'Value': 'xxxxxxxx'
        },
        {
            'Key': 'Purpose',
            'Value': 'Business'
        },
        {
            'Key': 'Name',
            'Value': 'xxxxxxxx'
        },
        {
            'Key': 'ApplicationRole',
            'Value': 'Load Balancer'
        },
        {
            'Key': 'Environment',
            'Value': 'travel-prod'
        },
        {
            'Key': 'Product',
            'Value': 'xxxxxxxx'
        }        
    ])
    print(response)


def main():
    alb_client = get_alb_client()
    add_alb_tags(alb_client)

if __name__ == "__main__":
    main()

