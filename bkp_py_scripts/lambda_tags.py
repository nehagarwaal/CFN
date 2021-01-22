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
    Resource='arn:aws:lambda:us-east-1:095218890333:function:flights_rabbitmq_nodes',
    Tags=
        {
                'ApplicationOwner': 'pkawale@tavisca.com',
                'ProductOwner': 'pkawale@tavisca.com',
                'Purpose': 'Business',
                'Name': 'flights_rabbitmq_nodes',
                'ApplicationRole': 'Lambda function',
                'Environment': 'travel-prod',
                'Product': 'Flights'            
        }      
    )
    print(response)


def main():
    lambda_client = get_lambda_client()
    add_lambda_tags(lambda_client)

if __name__ == "__main__":
    main()

