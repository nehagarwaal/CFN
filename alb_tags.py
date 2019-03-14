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
        'arn:aws:elasticloadbalancing:us-east-1:095218890333:loadbalancer/app/flight-stats-ALB/0e4263fc224a3fca',
    ],
    Tags=[
        {
            'Key': 'ApplicationOwner',
            'Value': 'pkawale@tavisca.com'
        },
        {
            'Key': 'ProductOwner',
            'Value': 'pkawale@tavisca.com'
        },
        {
            'Key': 'Purpose',
            'Value': 'Business'
        },
        {
            'Key': 'Name',
            'Value': 'flight-stats-ALB'
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
            'Value': 'Flights'
        }        
    ])
    print(response)


def main():
    alb_client = get_alb_client()
    add_alb_tags(alb_client)

if __name__ == "__main__":
    main()

