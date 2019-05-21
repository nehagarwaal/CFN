import boto3
import os
import sys
import get_mem_instance

#ECS Cluster Name
cluster_name = str(os.environ["cluster_name"])

#CPU Cores assigned to largest container
container_cpu_cores = str(os.environ["container_cpu_cores"])

#Soft Limit assigned to largest container
container_soft_limit = str(os.environ["container_soft_limit"])

#Create boto3 ECS Client
def get_ecs_client():
    client = boto3.client("ecs")
    return client

#Create cloudwatch ECS Client
def get_cloudwatch_client():
    client = boto3.client("cloudwatch")
    return client

#Calculates maximum count of largest container that can be accomodated per EC2 Instance
def container_scale_up_availability(remaining_cpu,remaining_memory):
    containers_by_cpu = int(remaining_cpu)//int(container_cpu_cores)
    containers_by_memory = int(remaining_memory)//int(container_soft_limit)
    container_capacity_per_instance = int(min(containers_by_cpu,containers_by_memory))
    return container_capacity_per_instance
    
#Calculates the total conatiner scale up capacity in the ECS Cluster
def get_remaining_resources_in_container_instances(ecs_client):
    response_arns = ecs_client.list_container_instances(
    cluster = cluster_name,
    filter='agentConnected == true'
    )
    container_instance_arns = response_arns.get("containerInstanceArns")
    instance_ids_in_ecs = []
    remaining_cpu = []
    remaining_memory = []
    container_availability_per_instance = []
    response = ecs_client.describe_container_instances(
    cluster=cluster_name,
    containerInstances=container_instance_arns
    )
    i = 0
    for container_instance_arn in container_instance_arns:
        instance_id = response.get("containerInstances")[i].get("ec2InstanceId")
        remaining_cpu_in_instance = response.get("containerInstances")[i].get("remainingResources")[0].get("integerValue")
        remaining_memory_in_instance = response.get("containerInstances")[i].get("remainingResources")[1].get("integerValue")
        instance_ids_in_ecs.append(instance_id)
        remaining_cpu.append(remaining_cpu_in_instance)
        remaining_memory.append(remaining_memory_in_instance)
        container_scale_up_count = container_scale_up_availability(remaining_cpu_in_instance,remaining_memory_in_instance)
        container_availability_per_instance.append(container_scale_up_count)
        i = i+1
    del container_instance_arn
    print(instance_ids_in_ecs)
    print(remaining_cpu)
    print(remaining_memory)
    print(container_availability_per_instance)
    total_scale_up_capacity_cluster = sum(container_availability_per_instance) 
    return get_metric_data_structure(total_scale_up_capacity_cluster)

#Puts data points to custom Cloudwatch Metrics
def put_metrics_to_cloudwatch(cw_client,cloudwatch_data):
    try:
        cw_client.put_metric_data(
        Namespace = "Scale_Up_Capacity_Cluster",
        MetricData=[cloudwatch_data]
        )
    except:
        print(sys.exc_info)
        pass

#Create custom Cloudwatch Metrics
def get_metric_data_structure(value):
    data = {
        "MetricName" : "Scale_Up_Capacity",
        "Value":value,
        "Unit": "Count",
        "Dimensions": [
                {
                    "Name": cluster_name,
                    "Value": cluster_name
                },
            ]
    }
    return data

#Entry point
def lambda_handler(event, context):
    ecs_client = get_ecs_client()
    cw_client = get_cloudwatch_client()
    cloudwatch_data = get_remaining_resources_in_container_instances(ecs_client)
    print(cloudwatch_data)
    put_metrics_to_cloudwatch(cw_client,cloudwatch_data)
