import requests
import boto3
import sys
import os
import json


def get_ec2_client():
    client = boto3.client("ec2")
    return client

def add_ec2_tags(ec2_client):
    response = ec2_client.create_tags(
    Resources=[
        'i-0749c2995a810daec',
        'i-0eb80439ce0fe406d',
        'i-0ed4e800c4827a89e'
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
            'Value': 'Flights-RabbitMQ'
        },
        {
            'Key': 'ApplicationRole',
            'Value': 'app-Server'
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
    ec2_client = get_ec2_client()
    add_ec2_tags(ec2_client)

if __name__ == "__main__":
    main()

