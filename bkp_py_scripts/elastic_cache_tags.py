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
     ResourceName='arn:aws:elasticache:us-east-1:346319152574:cluster:flights',
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
            'Value': 'flights'
        },
        {
            'Key': 'ApplicationRole',
            'Value': 'Cache'
        },
        {
            'Key': 'Environment',
            'Value': 'travel-qa'
        },
        {
            'Key': 'Product',
            'Value': 'Flights'
        }        
     ]
    )
    print(response)


def main():
    ec_client = get_ec_client()
    add_ec_tags(ec_client)

if __name__ == "__main__":
    main()

