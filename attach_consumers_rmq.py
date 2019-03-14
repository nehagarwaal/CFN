import requests
from requests.auth import HTTPBasicAuth
import boto3
import os
import json

rabbitmq_endpoint = "http://xxxx"
rabbitmq_username = "xx"
rabbitmq_password = "xx"
rabbitmq_port = "xxx"
rabbitmq_virtual_host = "xx"
rabbitmq_queue_name = "xx"
ecs_cluster_name = "xx"
ecs_service_name = "xx"

#Creating ECS boto3 client
def get_ecs_client():
    client = boto3.client("ecs")
    return client

#Creating ALB boto3 client
def get_alb_client():
    client = boto3.client("elbv2")
    return client

#Creating Application autoscaling boto3 client
def get_service_autoscaling_count():
    client = boto3.client("application-autoscaling")
    return client

#Obtaining number of consumers on specified queue
def get_consumer_count(route):
    queue_details = make_api_request(route)
    consumer_count = queue_details.get("consumers")
    return consumer_count

#Obtaining specified queue details
def make_api_request(route):
    try:
        url = "{}{}".format(rabbitmq_endpoint+":"+rabbitmq_port,route)
        print(url)
        response = requests.get(url,auth=(rabbitmq_username,rabbitmq_password))
        response_data = json.loads(response.text)
        return response_data
    except Exception as e:
        print(str(e))

#Obtaining number of containers currently running in ECS Service
def get_ecs_service_task_count(ecs_client):
    response = ecs_client.list_tasks(
        cluster = ecs_cluster_name,
        serviceName = ecs_service_name
    )
    service_task_count = len(response.get("taskArns"))
    return service_task_count

#Obtaining an array listing out health statuses of all targets in the TG
def get_tg_health_status(alb_client,target_group_arn):
    response = alb_client.describe_target_health(
        TargetGroupArn = target_group_arn
    )
    targets = response.get("TargetHealthDescriptions")
    target_health = []
    for target in targets:
            target_health.append(target.get("TargetHealth").get("State"))
    return target_health

#Obtaining True if all targets in the TG are healthy
def check_all_targets_health(target_group_health):
    all_targets_healthy = True 
    for target_health in target_group_health:
        if target_health != "healthy":
            all_targets_healthy = False
            break
    return all_targets_healthy

#Obtaining Target group ARN
def get_taget_group_arn(ecs_client):
    response = ecs_client.describe_services(
    cluster = ecs_cluster_name,
    services=[ecs_service_name]
    )
    target_group_arn = response.get("services")[0].get("loadBalancers")[0].get("targetGroupArn")
    return target_group_arn  

#Updating the ECS Service
def update_ecs_service(ecs_scaling_client,service_task_count):
    response_describe = ecs_scaling_client.describe_scalable_targets(
    ServiceNamespace="ecs",
    ResourceIds = ["service/Flights-Engine/Engine-WorkerAPP"],
    ScalableDimension='ecs:service:DesiredCount'
    ) 
    minimum_containers = response_describe.get("ScalableTargets")[0].get("MinCapacity")
    maximum_containers = response_describe.get("ScalableTargets")[0].get("MaxCapacity")
    if service_task_count == maximum_containers:
        response_update = ecs_scaling_client.register_scalable_target(
        ServiceNamespace = "ecs",
        ResourceId = "xxxx",
        ScalableDimension = 'ecs:service:DesiredCount',        
        MaxCapacity = maximum_containers + 2,
        MinCapacity = minimum_containers + 1,
        RoleARN = "arn:aws:iam::922451091924:role/spinnakerRole"
        )
    elif service_task_count < maximum_containers:
        response_update = ecs_scaling_client.register_scalable_target(
        ServiceNamespace = "ecs",
        ResourceId = "xxxx",
        ScalableDimension = 'ecs:service:DesiredCount',
        MinCapacity = minimum_containers + 1,
        MaxCapacity = maximum_containers + 1,
        RoleARN = "xxx"
        )
        print(response_update)

def main():
    ecs_client = get_ecs_client()
    alb_client = get_alb_client()
    ecs_scaling_client = get_service_autoscaling_count()
    queue_consumer_count = get_consumer_count("/api/queues/" + rabbitmq_virtual_host + "/" + rabbitmq_queue_name)
    service_task_count = get_ecs_service_task_count(ecs_client)
    target_group_arn = get_taget_group_arn(ecs_client)
    target_group_health = get_tg_health_status(alb_client,target_group_arn)
    all_targets_healthy = check_all_targets_health(target_group_health)
    if all_targets_healthy == True and queue_consumer_count == 0:
        update_ecs_service(ecs_scaling_client,service_task_count)

        
if __name__ == "__main__":       
    main()
