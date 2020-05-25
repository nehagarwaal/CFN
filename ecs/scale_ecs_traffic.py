import boto3
from datetime import datetime, timedelta, timezone
import math
import os

cluster_name = os.environ["cluster_name"]
service_name = os.environ["service_name"]
service_container_base_value = int(os.environ["service_container_base_value"])
waf_web_acl = os.environ["waf_web_acl"]
waf_rule = os.environ["waf_rule"]

ecs_client = boto3.client('ecs')
cw_client = boto3.client('cloudwatch')
as_client = boto3.client('application-autoscaling')

def get_metric_data():
    # PresentTime=pd.to_datetime(datetime.utcnow().strftime("%Y-%m-%d, %H:%M"))
    datetime_object = datetime.utcnow()
    PresentTime=datetime(datetime_object.year,datetime_object.month,datetime_object.day,datetime_object.hour,datetime_object.minute)
    response = cw_client.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'waf_allowed_requests',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'WAF',
                        'MetricName': 'AllowedRequests',
                        'Dimensions': [
                            {
                                'Name': 'Region',
                                'Value': 'us-east-1'
                            },
                            {
                                'Name': 'Rule',
                                'Value': waf_rule
                            },
                            {
                                'Name': 'WebACL',
                                'Value': waf_web_acl
                            }                       
                        ]
                    },
                    'Period': 60,
                    'Stat': 'Sum'
                },
                'Label': 'string'
            }
        ],
        StartTime= PresentTime - timedelta(minutes=10),
        EndTime=PresentTime
    )
    rpm = response.get("MetricDataResults")[0].get("Values")
    rps = [math.ceil(x / 60) for x in rpm]
    print(rpm)
    print(rps)
    print(PresentTime - timedelta(minutes=10), PresentTime)
    return rps

def get_task_definition_and_desired_count():
    response = ecs_client.describe_services(
        cluster=cluster_name,
        services=[
            service_name,
        ]
    )
    desired_count = response.get("services")[0].get("desiredCount")
    global task_definition 
    task_definition = response.get("services")[0].get("taskDefinition")
    print(task_definition)
    return desired_count

def get_min_count():
    response = as_client.describe_scalable_targets(
        ServiceNamespace='ecs',
        ResourceIds=["service/" + cluster_name + "/" + service_name],
        ScalableDimension='ecs:service:DesiredCount'
    )
    min_count = response.get("ScalableTargets")[0].get("MinCapacity")
    return min_count

def update_ecs_service(new_desired_count):
    response = ecs_client.update_service(
        cluster=cluster_name,
        service=service_name,
        desiredCount=new_desired_count,
        taskDefinition=task_definition,
        deploymentConfiguration={
            'maximumPercent': 200,
            'minimumHealthyPercent': 100
        },
        healthCheckGracePeriodSeconds=0
    )   
    print(response)


def lambda_handler(event, context):
    load_rps = get_metric_data()
    new_desired_count = 0
    current_desired_count = get_task_definition_and_desired_count()
    container_min_count = get_min_count()
    if len(load_rps) != 0: 
    
        if max(load_rps) == 1:
            new_desired_count = container_min_count
        else:
            new_desired_count = service_container_base_value*(max(load_rps)) #ScaleDown
        print("*****New Count "+str(new_desired_count))
        if new_desired_count != 0 and current_desired_count != new_desired_count and new_desired_count >= container_min_count:
            print("*****Updating ECS Service with " + str(new_desired_count) + " containers*****")
            update_ecs_service(new_desired_count)
    elif current_desired_count != container_min_count:                      #SetToMinCount           
        update_ecs_service(container_min_count)
    else:
        print("List was empty, no actions to be performed")
