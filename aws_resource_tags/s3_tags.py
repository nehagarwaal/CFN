import requests
import boto3
import sys
import os
import json

def add_s3_tags(bucket_tagging):
    response = bucket_tagging.put(
    Tagging={
        'TagSet': [
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
            'Value': 'S3Bucket'
        },
        {
            'Key': 'Environment',
            'Value': 'xxxxxxxx'
        },
        {
            'Key': 'Product',
            'Value': 'Flights'
        }
        ]
    }
    )
    print(response)


def main():
    s3 = boto3.resource('s3')
    bucket_tagging = s3.BucketTagging('xxxxxxxx')
    add_s3_tags(bucket_tagging)
if __name__ == "__main__":
    main()

