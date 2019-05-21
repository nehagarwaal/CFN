import requests
import boto3
import sys
import os
import json


def get_lambda_client():
    client = boto3.client("lambda")
    return client

def add_lambda_tags(lambda_client):
    response = lambda_client.tag_resource(
    Resource='arn:aws:xxxxxxxx',
    Tags=
        {
                'ApplicationOwner': 'xxxxxxxx',
                'ProductOwner': 'xxxxxxxx',
                'Purpose': 'xxxxxxxx',
                'Name': 'xxxxxxxx',
                'ApplicationRole': 'Lambda function',
                'Environment': 'xxxxxxxx',
                'Product': 'xxxxxxxx'            
        }      
    )
    print(response)


def main():
    lambda_client = get_lambda_client()
    add_lambda_tags(lambda_client)

if __name__ == "__main__":
    main()

