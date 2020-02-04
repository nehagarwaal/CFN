import boto3
from datetime import date
from datetime import timedelta
from datetime import datetime
import pandas as pd
import openpyxl

def get_iam_client():
    client = boto3.client("iam")
    return client

def get_iam_resource():
    resource = boto3.resource("iam")
    return resource

def list_of_old_access_keys(iam_client, iam_resource):
    current_date = date.today()
    max_access_key_age = timedelta(days=90)
    access_ids = []
    user_names = []
    access_keys_age = []
    access_keys_status = []
    for user in iam_resource.users.all():
        Metadata = iam_client.list_access_keys(UserName=user.user_name)
        if Metadata['AccessKeyMetadata'] :
            for key in user.access_keys.all():
                AccessId = key.access_key_id
                Status = key.status
                access_key_date = iam_client.list_access_keys(UserName=user.user_name)['AccessKeyMetadata'][0]['CreateDate'].date()
                access_key_age = current_date - access_key_date     
                if access_key_age.days > max_access_key_age.days:
                    access_ids.append(AccessId)
                    user_names.append(user.user_name)
                    access_keys_age.append(access_key_age.days)
                    access_keys_status.append(Status)
    df = pd.DataFrame() 
    df['AccessIds'] = access_ids
    df['UserNames'] = user_names
    df['AccessKeysAge'] = access_keys_age
    df['AccessKeysStatus'] = access_keys_status
    df.to_excel('stage.xlsx', index = False) 

def main():
    iam_client = get_iam_client()
    iam_resource = get_iam_resource()
    list_of_old_access_keys(iam_client, iam_resource)

if __name__ == "__main__":
    main()
