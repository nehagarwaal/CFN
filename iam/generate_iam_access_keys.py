import boto3
import pandas as pd
import openpyxl
import sys

user_name = sys.argv[1]

def get_iam_client():
    client = boto3.client("iam")
    return client

def generate_iam_accesskey(iam_client):
    response = iam_client.create_access_key(
    UserName=user_name
    )
    return response

def create_csv(accesskey, secretkey):
    d = {'AccessKey': [accesskey], 'SecretKey': [secretkey]}
    df = pd.DataFrame(data=d) 
    df.to_excel('keys.xlsx', index = False)     

def main():
    iam_client = get_iam_client()
    keys = generate_iam_accesskey(iam_client)
    accesskey = keys.get("AccessKey").get("AccessKeyId")
    secretkey = keys.get("AccessKey").get("SecretAccessKey")
    create_csv(accesskey, secretkey)

if __name__ == "__main__":
    main()
