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
     ResourceName='xx',
     Tags=[
        {
            'Key': 'ApplicationOwner',
            'Value': 'xx'
        },
        {
            'Key': 'ProductOwner',
            'Value': 'xx'
        },
        {
            'Key': 'Purpose',
            'Value': 'xx'
        },
        {
            'Key': 'Name',
            'Value': 'xx'
        },
        {
            'Key': 'ApplicationRole',
            'Value': 'xx'
        },
        {
            'Key': 'Environment',
            'Value': 'xx'
        },
        {
            'Key': 'Product',
            'Value': 'xx'
        }        
     ]
    )
    print(response)


def main():
    ec_client = get_ec_client()
    add_ec_tags(ec_client)

if __name__ == "__main__":
    main()
