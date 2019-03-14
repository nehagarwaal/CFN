import requests
import boto3
import sys
import os
import json


def get_ec_client():
    client = boto3.client("elasticache")
    return client

def add_ec_tags(ec_client):
    response = ec_client.add_tags_to_resource(
    ResourceName=[
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
            'Value': 'Cache'
        },
        {
            'Key': 'Environment',
            'Value': 'xxxxxxxx'
        },
        {
            'Key': 'Product',
            'Value': 'xxxxxxxx'
        }        
    ])
    print(response)


def main():
    ec_client = get_ec_client()
    add_ec_tags(ec_client)

if __name__ == "__main__":
    main()

