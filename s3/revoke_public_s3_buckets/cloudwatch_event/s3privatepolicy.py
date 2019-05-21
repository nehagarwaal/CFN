import boto3
import list_of_public_buckets
import json
import sys

s3_bucket_name = "test-private-test"

#Create S3 Client
def get_s3_client():
    client = boto3.client("s3")
    return client

#Get ACL access status (public/private)
def get_s3_bucket_acl(s3_client):
    all_acl = s3_client.get_bucket_acl(Bucket=s3_bucket_name)
    grants = all_acl.get("Grants")
    is_acl_public = False
    for each_grant in grants:
        grantee_type = each_grant.get("Grantee").get("Type")
        grantee_uri = each_grant.get("Grantee").get("URI")
        if (grantee_type == "Group" and grantee_uri == 'http://acs.amazonaws.com/groups/global/AllUsers'):
            is_acl_public = True
            break
    return is_acl_public

#Update S3 bucket policy if it makes s3 bucket's access public
def update_s3_bucket_policy(s3_client):
    statements_to_delete = []
    statements_in_bucket_policy = []
    response = (s3_client.get_bucket_policy(Bucket=s3_bucket_name)).get("Policy")
    bucket_policy = json.loads(str(response))
    for statement in bucket_policy.get("Statement"):
        if statement.get("Principal") == '*':
            statements_to_delete.append(statement)  
    if len(statements_to_delete) == len(bucket_policy.get("Statement")):
        s3_client.delete_bucket_policy(Bucket=s3_bucket_name)
    else:
        i = 0
        statements_in_bucket_policy = bucket_policy.get("Statement")
        for statement1 in statements_in_bucket_policy:
            for statement2 in statements_to_delete:
                if statement2 == statement1:
                    statements_in_bucket_policy.pop(i)
                else:
                    i = i+1
        print(statements_in_bucket_policy)
        updated_bucket_policy = {
            "Version": "2012-10-17",
            "Statement": statements_in_bucket_policy 
            }
        updated_bucket_policy_json = json.dumps(updated_bucket_policy)
        s3_client.put_bucket_policy(
            Bucket=s3_bucket_name,
            Policy=updated_bucket_policy_json
        )        

#Update S3 bucket's ACL if it is public. Refer to get_s3_bucket_acl()
def update_s3_bucket_access(s3_client):
    response = s3_client.put_bucket_acl(
    ACL='private',
    Bucket=s3_bucket_name
    )
    print("Public access removed")

#Entry point
def lambda_handler(event, context): 
    if s3_bucket_name not in list_of_public_buckets.public_s3_buckets:
        s3_client = get_s3_client()
        is_acl_public = get_s3_bucket_acl(s3_client)
        if is_acl_public == True:
            update_s3_bucket_access(s3_client)
        try:
            is_public = s3_client.get_bucket_policy_status(Bucket=s3_bucket_name)            
            if is_public.get("PolicyStatus").get("IsPublic") == True:
                update_s3_bucket_policy(s3_client)
        except:
            print(sys.exc_info)
            pass