import boto3
import json
import logging
import sys

log = logging.getLogger()
log.setLevel(logging.DEBUG)
APPLICABLE_RESOURCES = ["AWS::S3::Bucket"]

class Check_complaince():

    #Get s3 client
    def get_s3_client(self):
        try:
            s3_client = boto3.client("s3")
            return s3_client
        except:
            print("Access denied, check permissions")

    #Get config client
    def get_config_client(self):
        try:
            config_client = boto3.client("config")
            return config_client
        except:
            print("Access denied, check permissions")
    
    #Evaluate if bucket policy makes the bucket public
    def evaluate_bucket_policy_compliance(self, configuration_item, s3_client, bucket_name):
        bucket_policy = configuration_item["supplementaryConfiguration"].get("BucketPolicy")
        if bucket_policy['policyText'] is not None:
            bucket_policy_status = s3_client.get_bucket_policy_status(Bucket=bucket_name)
            if bucket_policy_status.get("PolicyStatus").get("IsPublic") == True:
                return {
                    "compliance_type": "NON_COMPLIANT",
                    "annotation": 'Bucket Policy is public',
                    "flag": False
                }
            else:
                return {
                    "compliance_type": "COMPLIANT",
                    "annotation": 'Bucket Policy is private',
                    "flag": True
                }

        else:
            return {
                "compliance_type": "NOT_APPLICABLE",
                "annotation": 'Bucket Policy does not exist',
                "flag": True
            }

    #Evaluate if ACL makes the bucket public
    def evaluate_acl_compliance(self, configuration_item, s3_client, bucket_name):
        all_acl = s3_client.get_bucket_acl(Bucket=bucket_name)    
        grants = all_acl.get("Grants")
        is_acl_public = False
        for each_grant in grants:
            grantee_type = each_grant.get("Grantee").get("Type")
            grantee_uri = each_grant.get("Grantee").get("URI")
            if (grantee_type == "Group" and grantee_uri == 'http://acs.amazonaws.com/groups/global/AllUsers'):
                is_acl_public = True
                break
        if is_acl_public == True:
            return {
                "compliance_type": "NON_COMPLIANT",
                "annotation": "ACL is public",
                "flag": False
            }
        else:
            return {
                    "compliance_type": "COMPLIANT",
                    "annotation": 'ACL is private',
                    "flag": True
                }  

    #Put status of bucket compliance to AWS config
    def put_compliance_status_to_aws_config(self, bucket_compliance, config_client, invoking_event, event):
        if False in bucket_compliance:  
            config_client.put_evaluations(
            Evaluations=[
            {
                'ComplianceResourceType':    invoking_event['configurationItem']['resourceType'],
                'ComplianceResourceId':      invoking_event['configurationItem']['resourceId'],
                'ComplianceType':            "NON_COMPLIANT",
                "Annotation":                "Bucket is public",
                'OrderingTimestamp':         invoking_event['configurationItem']['configurationItemCaptureTime']
            },
            ],
            ResultToken=event['resultToken'])
        else:
            config_client.put_evaluations(
            Evaluations=[
                {
                    'ComplianceResourceType':    invoking_event['configurationItem']['resourceType'],
                    'ComplianceResourceId':      invoking_event['configurationItem']['resourceId'],
                    'ComplianceType':            "COMPLIANT",
                    "Annotation":                "Bucket is private",
                    'OrderingTimestamp':         invoking_event['configurationItem']['configurationItemCaptureTime']
                },
            ],
            ResultToken=event['resultToken']) 

#Entry point
def lambda_handler(event, context):
    log.debug('Event %s', event)
    invoking_event               = json.loads(event['invokingEvent'])
    configuration_item           = invoking_event["configurationItem"]
    bucket_compliance            = []
    bucket_compliance_annotation = []
    ob                           = Check_complaince()
    s3_client                    = ob.get_s3_client()
    bucket_name                  = invoking_event.get("configurationItem").get("configuration").get("name")    
    s3_client.download_file('cnx-nextgen-devops', 'public_s3_bucket_list/qa_list_of_public_buckets.py', '/tmp/qa_list_of_public_buckets.py')
    sys.path.append('/tmp/')
    import qa_list_of_public_buckets
    if bucket_name not in qa_list_of_public_buckets.public_s3_buckets:
        if configuration_item["resourceType"] in APPLICABLE_RESOURCES and configuration_item['configurationItemStatus'] != "ResourceDeleted":
            evaluation_bucket_policy = ob.evaluate_bucket_policy_compliance(configuration_item, s3_client, bucket_name)
            evaluation_acl           = ob.evaluate_acl_compliance(configuration_item, s3_client, bucket_name)

            bucket_compliance.append(evaluation_bucket_policy["flag"])
            bucket_compliance_annotation.append(evaluation_bucket_policy["annotation"])
            bucket_compliance.append(evaluation_acl["flag"])
            bucket_compliance_annotation.append(evaluation_acl["annotation"])
      
        elif configuration_item["resourceType"] not in APPLICABLE_RESOURCES or configuration_item['configurationItemStatus'] == "ResourceDeleted":
            resource_evaluation = {
                "compliance_type": "NOT_APPLICABLE",
                "annotation": "The rule doesn't apply to resources of type " + configuration_item["resourceType"] + "as either the resource is inapplicable or is deleted.",
                "flag": True
            }
            bucket_compliance.append(resource_evaluation["flag"])
            bucket_compliance_annotation.append(resource_evaluation["annotation"])

        config_client = ob.get_config_client()
        ob.put_compliance_status_to_aws_config(bucket_compliance, config_client, invoking_event, event)

