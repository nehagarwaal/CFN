import boto3
from datetime import datetime, timedelta, timezone
import math
import os

cluster_name ="Flights-Engine-V2"
service_name ="Engine-V2-WorkerAPP"
service_container_base_value = 4
waf_web_acl ="FlightsEngineACL"
waf_rule = "FlightsChaseInitRule"

ecs_client = boto3.client('ecs')
cw_client = boto3.client('cloudwatch')
as_client = boto3.client('application-autoscaling')

def get_min_count():
    response = as_client.describe_scalable_targets(
        ServiceNamespace='ecs',
        ResourceIds=["service/" + cluster_name + "/" + service_name],
        ScalableDimension='ecs:service:DesiredCount'
    )
    min_count = response.get("ScalableTargets")[0].get("MinCapacity")
    return min_count

def get_metric_data():
    PresentTime=datetime.utcnow()
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
    print(response)

def get_task_definition_and_desired_count():
    response = ecs_client.describe_services(
        cluster=cluster_name,
        services=[
            service_name,
        ]
    )
    print(response)
    desired_count = response.get("services")[0].get("desiredCount")
    global task_definition 
    task_definition = response.get("services")[0].get("taskDefinition")
    print(task_definition)
    return desired_count

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


def main():
    # get_min_count()
    load_rps = get_metric_data()
    # get_task_definition_and_desired_count()
    # new_desired_count = 0
    # if max(load_rps) < load_rps[0]:
    #     new_desired_count = service_container_base_value*load_rps[0] #ScaleUp
    # elif max(load_rps) > load_rps[0] :
    #     new_desired_count = get_task_definition_and_desired_count() - 1 #ScaleDown
    # elif all(i == load_rps[0] for i in load_rps):
    #         new_desired_count = service_container_base_value*load_rps[0]
    # if new_desired_count != 0 : #NoActionRequired
    #     update_ecs_service(new_desired_count)

if __name__ == "__main__":
    main()
