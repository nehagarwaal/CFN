import boto3
import json
import sys
import logging

log = logging.getLogger()
log.setLevel(logging.DEBUG)

class Revoke_public_s3():

    #Get s3 client
    def get_s3_client(self):
        try:
            s3_client = boto3.client("s3")
            return s3_client
        except:
            print("Access denied, check permissions")

    #Get SSM client
    def get_ssm_client(self):
        try:
            ssm_client = boto3.client("ssm")
            return ssm_client
        except:
            print("Access denied, check permissions")

    #Get SNS Client
    def get_sns_client(self):
        try:
            sns_client = boto3.client('sns')
            return sns_client
        except:
            print("Access denied, check permissions")

    #Send email to notify   
    def publish_msg_to_sns(self, sns_client, s3_bucket_name):
        s3_bucket_name = s3_bucket_name
        sns_client.publish(
            TopicArn='arn:aws:sns:us-east-1:346319152574:revoke_public_s3_buckets',
            Message='S3 bucket "' + s3_bucket_name + '" was made public on p-qa account. It has been made private.',
            Subject='Revoked public S3 Bucket',
            MessageStructure='testfromscript'
        )

    #Get list of compliance status from SSM Parameter Store [bucket_policy, acl]
    def get_complaince_status_from_parameterstore(self, ssm_client, s3_bucket_name):
        parameter_store_key = "s3_public_compliance_" + s3_bucket_name
        parameter_response = ssm_client.get_parameter(
        Name=parameter_store_key
        )
        return parameter_response.get("Parameter").get("Value")

    #Delete list of compliance status from SSM Parameter Store [bucket_policy, acl]
    def delete_complaince_status_from_parameterstore(self, ssm_client, s3_bucket_name):
        parameter_store_key = "s3_public_compliance_" + s3_bucket_name
        ssm_client.delete_parameter(
        Name=parameter_store_key
        )
        print("Parameter store key deleted")

    #Update S3 bucket policy if it makes s3 bucket's access public
    def update_s3_bucket_policy(self, s3_client, s3_bucket_name):
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
    def update_s3_bucket_acl(self, s3_client, s3_bucket_name):
        s3_client.put_bucket_acl(
        ACL='private',
        Bucket=s3_bucket_name
        )
        print("Public access removed from bucket ACL")

#Entry point
def lambda_handler(event, context):
    log.debug('Event %s', event)
    ob                        = Revoke_public_s3()
    s3_client                 = ob.get_s3_client()
    s3_bucket_name            = (json.loads(json.dumps(event))).get("s3_bucket_name")
    ssm_client                = ob.get_ssm_client()
    bucket_compliance         = list(ob.get_complaince_status_from_parameterstore(ssm_client, s3_bucket_name).split(","))
    if str(bucket_compliance[0]) == str(False):
        ob.update_s3_bucket_policy(s3_client, s3_bucket_name)
    if str(bucket_compliance[1]) == str(False):
        ob.update_s3_bucket_acl(s3_client, s3_bucket_name)
    sns_client                = ob.get_sns_client()
    ob.delete_complaince_status_from_parameterstore(ssm_client, s3_bucket_name)
    ob.publish_msg_to_sns(sns_client, s3_bucket_name)
