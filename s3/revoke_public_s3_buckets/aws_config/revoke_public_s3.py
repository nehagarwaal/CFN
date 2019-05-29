import boto3
import json
import sys
import logging

log = logging.getLogger()
log.setLevel(logging.DEBUG)

#Create S3 Client
def get_s3_client():
    client = boto3.client("s3")
    return client

#Create SNS Client
def get_sns_client():
    sns_client = boto3.client('sns')
    return sns_client

#Send email to notify 
def publish_msg_to_sns(sns_client, s3_bucket_name):
    s3_bucket_name = "test-private-test"
    sns_client.publish(
        TopicArn='arn:aws:sns:us-east-1:346319152574:revoke_public_s3_buckets',
        Message='S3 bucket "' + s3_bucket_name + '" was made public on p-qa account. It has been made private.',
        Subject='Revoked public S3 Bucket',
        MessageStructure='testfromscript'
    )

#Update S3 bucket policy if it makes s3 bucket's access public
def update_s3_bucket_policy(s3_client, s3_bucket_name):
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
def update_s3_bucket_acl(s3_client, s3_bucket_name):
    s3_client.put_bucket_acl(
    ACL='private',
    Bucket=s3_bucket_name
    )
    print("Public access removed from bucket ACL")

#Entry point
def lambda_handler(event, context):
        print(event)
        log.debug('Event %s', event)
        s3_bucket_name = (json.loads(json.dumps(event))).get("s3_bucket_name")
        s3_client = get_s3_client()
        all_acl = s3_client.get_bucket_acl(Bucket=s3_bucket_name)    
        grants = all_acl.get("Grants")
        is_acl_public = False
        for each_grant in grants:
            grantee_type = each_grant.get("Grantee").get("Type")
            grantee_uri = each_grant.get("Grantee").get("URI")
            if (grantee_type == "Group" and grantee_uri == 'http://acs.amazonaws.com/groups/global/AllUsers'):
                is_acl_public = True
                break
        if is_acl_public == True:
                update_s3_bucket_acl(s3_client, s3_bucket_name)                
        try:
            is_policy_public = s3_client.get_bucket_policy_status(Bucket=s3_bucket_name)            
            if is_policy_public.get("PolicyStatus").get("IsPublic") == True:
                update_s3_bucket_policy(s3_client, s3_bucket_name)
        except:
            print(sys.exc_info)
            pass
        sns_client = get_sns_client()
        publish_msg_to_sns(sns_client, s3_bucket_name)
