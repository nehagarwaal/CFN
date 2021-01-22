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
        'i-02bca6cb4a7960dd6',
        'i-07849b66498ad8fae',
        'i-01765285b388548ef'
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
            'Value': 'Flights-RMQ-SSL'
        },
        {
            'Key': 'ApplicationRole',
            'Value': 'app-Server'
        },
        {
            'Key': 'Environment',
            'Value': 'travel-stage'
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

