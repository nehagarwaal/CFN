import boto3
import get_mem_instance

cluster_name = "Flights-Engine-V2"
cpu_cores_assigned_to_containers = 1
soft_limit_of_container = 1536

def get_ecs_client():
    client = boto3.client("ecs")
    return client

def get_ec2_client():
    client = boto3.client("ec2")
    return client

def get_asg_client():
    asg_client = boto3.client('autoscaling')
    return asg_client

def get_asg_name(asg_client):
    response = asg_client.describe_tags(
    Filters=[
        {
            'Name': 'value',
            'Values': [cluster_name]
        }
      ]
    )
    asg_name = response.get("Tags")[0].get("ResourceId")
    return asg_name

def get_container_capacity_per_instance(asg_client, ec2_client, asg_name):
    asg_response = asg_client.describe_auto_scaling_groups(
    AutoScalingGroupNames=[
        asg_name,
    ]
    )
    instance_id = asg_response.get("AutoScalingGroups")[0].get("Instances")[0].get("InstanceId")
    ec2_response = ec2_client.describe_instances(
    InstanceIds=[instance_id]
    )

    instance_type = ec2_response.get("Reservations")[0].get("Instances")[0].get("InstanceType")
    instance_cpu_cores = ec2_response.get("Reservations")[0].get("Instances")[0].get("CpuOptions").get("CoreCount")
    
    containers_by_cpu = int(instance_cpu_cores//cpu_cores_assigned_to_containers)
    containers_by_memory = (get_mem_instance.memory[instance_type]*1024)//soft_limit_of_container
    container_capacity_per_instance = min(containers_by_cpu,containers_by_memory)
    return container_capacity_per_instance

def get_max_containers_in_instance(available_cpu, available_mem):
    containers_by_cpu = int(available_cpu//cpu_cores_assigned_to_containers)
    containers_by_memory = int(available_mem//soft_limit_of_container)
    container_capacity_per_instance = min(containers_by_cpu,containers_by_memory)
    return container_capacity_per_instance
    
def get_instances_in_cluster(ecs_client):
    response_arns = ecs_client.list_container_instances(
    cluster = cluster_name,
    filter='agentConnected == true'
    )
    container_instance_arns = response_arns.get("containerInstanceArns")
    instance_ids = []
    remaining_cpu = []
    remaining_memory = []
    response = ecs_client.describe_container_instances(
    cluster=cluster_name,
    containerInstances=container_instance_arns
    )
    i = 0
    for container_instance_arn in container_instance_arns:
        instance_id = response.get("containerInstances")[i].get("ec2InstanceId")
        remaining_cpu_instance = response.get("containerInstances")[i].get("remainingResources")[0].get("integerValue")
        remaining_memory_instance = response.get("containerInstances")[i].get("remainingResources")[1].get("integerValue")
        instance_ids.append(instance_id)
        remaining_cpu.append(remaining_cpu_instance)
        remaining_memory.append(remaining_memory_instance)
        i = i+1
    del container_instance_arn
    remaining_resources = {}
    remaining_resources["instance_ids"] = instance_ids
    remaining_resources["remaining_cpu"] = remaining_cpu
    remaining_resources["remaining_memory"] = remaining_memory
    return remaining_resources

def main():
    # asg_client = get_asg_client()
    # ec2_client = get_ec2_client()
    ecs_client = get_ecs_client()
    # asg_name = get_asg_name(asg_client)
    # container_capacity_per_instance = get_container_capacity_per_instance(asg_client, ec2_client, asg_name)
    instance_ids = get_instances_in_cluster(ecs_client)

if __name__ == "__main__":
    main()