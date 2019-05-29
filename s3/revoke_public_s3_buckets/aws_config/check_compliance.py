import boto3
import json
import logging
import sys

log = logging.getLogger()
log.setLevel(logging.DEBUG)
APPLICABLE_RESOURCES = ["AWS::S3::Bucket"]

#Get s3 client
def get_s3_client():
    client = boto3.client("s3")
    return client

#Evaluate if bucket policy makes the bucket public
def evaluate_bucket_policy_compliance(configuration_item, s3_client, bucket_name):
    if configuration_item["resourceType"] not in APPLICABLE_RESOURCES:
        return {
            "compliance_type": "NOT_APPLICABLE",
            "annotation": "The rule doesn't apply to resources of type " +
            configuration_item["resourceType"] + "."
        }

    if configuration_item['configurationItemStatus'] == "ResourceDeleted":
        return {
            "compliance_type": "NOT_APPLICABLE",
            "annotation": "The configurationItem was deleted " +
                          "and therefore cannot be validated"
        }

    bucket_policy = configuration_item["supplementaryConfiguration"].get("BucketPolicy")
    if bucket_policy['policyText'] is None:
        return {
            "compliance_type": "NOT_APPLICABLE",
            "annotation": 'Bucket Policy does not exists'
        }

    else:
        response = s3_client.get_bucket_policy_status(Bucket=bucket_name)
        if response.get("PolicyStatus").get("IsPublic") == True:
            return {
                "compliance_type": "NON_COMPLIANT",
                "annotation": 'Bucket Policy is public'
            }
        else:
            return {
                "compliance_type": "COMPLIANT",
                "annotation": 'Bucket Policy is private'
            }

#Evaluate if ACL makes the bucket public
def evaluate_acl_compliance(configuration_item, s3_client, bucket_name):
    if configuration_item["resourceType"] not in APPLICABLE_RESOURCES:
        return {
            "compliance_type": "NOT_APPLICABLE",
            "annotation": "The rule doesn't apply to resources of type " + configuration_item["resourceType"] + "."
        }

    if configuration_item['configurationItemStatus'] == "ResourceDeleted":
        return {
            "compliance_type": "NOT_APPLICABLE",
            "annotation": "The configurationItem was deleted and therefore cannot be validated"
        }
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
            "annotation": "ACL is public"
        }
    else:
        return {
                "compliance_type": "COMPLIANT",
                "annotation": 'Bucket ACL is private'
            }

#Entry point
def lambda_handler(event, context):
    log.debug('Event %s', event)
    invoking_event      = json.loads(event['invokingEvent'])
    configuration_item  = invoking_event["configurationItem"]
    bucket_name = invoking_event.get("configurationItem").get("configuration").get("name")
    s3_client = get_s3_client()
    s3_client.download_file('cnx-nextgen-devops', 'public_s3_bucket_list/qa_list_of_public_buckets.py', '/tmp/qa_list_of_public_buckets.py')
    sys.path.append('/tmp/')
    import qa_list_of_public_buckets
    if bucket_name not in qa_list_of_public_buckets.public_s3_buckets:
        evaluation_bucket_policy     = evaluate_bucket_policy_compliance(configuration_item, s3_client, bucket_name)
        evaluation_acl              = evaluate_acl_compliance(configuration_item, s3_client, bucket_name)
        config                       = boto3.client('config')

        if evaluation_bucket_policy["compliance_type"] == 'NON_COMPLIANT' and evaluation_acl["compliance_type"] != 'NON_COMPLIANT':    
            config.put_evaluations(
                Evaluations=[
                    {
                        'ComplianceResourceType':    invoking_event['configurationItem']['resourceType'],
                        'ComplianceResourceId':      invoking_event['configurationItem']['resourceId'],
                        'ComplianceType':            evaluation_bucket_policy["compliance_type"],
                        "Annotation":                evaluation_bucket_policy["annotation"],
                        'OrderingTimestamp':         invoking_event['configurationItem']['configurationItemCaptureTime']
                    },
                ],
                ResultToken=event['resultToken'])
    
        elif evaluation_acl["compliance_type"] == 'NON_COMPLIANT' and evaluation_bucket_policy["compliance_type"] != 'NON_COMPLIANT':    
            config.put_evaluations(
                Evaluations=[
                    {
                        'ComplianceResourceType':    invoking_event['configurationItem']['resourceType'],
                        'ComplianceResourceId':      invoking_event['configurationItem']['resourceId'],
                        'ComplianceType':            evaluation_acl["compliance_type"],
                        "Annotation":                evaluation_acl["annotation"],
                        'OrderingTimestamp':         invoking_event['configurationItem']['configurationItemCaptureTime']
                    },
                ],
                ResultToken=event['resultToken'])

        elif evaluation_bucket_policy["compliance_type"] == 'COMPLIANT' and evaluation_acl["compliance_type"] == 'COMPLIANT':    
            config.put_evaluations(
                Evaluations=[
                    {
                        'ComplianceResourceType':    invoking_event['configurationItem']['resourceType'],
                        'ComplianceResourceId':      invoking_event['configurationItem']['resourceId'],
                        'ComplianceType':            evaluation_bucket_policy["compliance_type"],
                        "Annotation":                'Both Bucket Policy and ACL are compliant (private)',
                        'OrderingTimestamp':         invoking_event['configurationItem']['configurationItemCaptureTime']
                    },
                ],
                ResultToken=event['resultToken'])
    
        elif evaluation_bucket_policy["compliance_type"] == 'NON_COMPLIANT' and evaluation_acl["compliance_type"] == 'NON_COMPLIANT':    
            config.put_evaluations(
                Evaluations=[
                    {
                        'ComplianceResourceType':    invoking_event['configurationItem']['resourceType'],
                        'ComplianceResourceId':      invoking_event['configurationItem']['resourceId'],
                        'ComplianceType':            evaluation_bucket_policy["compliance_type"],
                        "Annotation":                'Both Bucket Policy and ACL are non-compliant (public)',
                        'OrderingTimestamp':         invoking_event['configurationItem']['configurationItemCaptureTime']
                    },
                ],
                ResultToken=event['resultToken'])

        else:
            config.put_evaluations(
                Evaluations=[
                    {
                        'ComplianceResourceType':    invoking_event['configurationItem']['resourceType'],
                        'ComplianceResourceId':      invoking_event['configurationItem']['resourceId'],
                        'ComplianceType':            'NOT_APPLICABLE',
                        "Annotation":                'Either the resource type is inapplicable/deleted or bucket policy does not exist',
                        'OrderingTimestamp':         invoking_event['configurationItem']['configurationItemCaptureTime']
                    },
                ],
                ResultToken=event['resultToken'])
