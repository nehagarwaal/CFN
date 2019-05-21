import boto3

cluster_name = "Flights-Engine-V2"
cpu_cores_assigned_to_containers = 1.5
soft_limit_of_container = 1536

# def get_ecs_client():
#     client = boto3.client("ecs")
#     return client

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

def describe_asg(asg_client, ec2_client, asg_name):
    asg_response = asg_client.describe_auto_scaling_groups(
    AutoScalingGroupNames=[
        asg_name,
    ]
    )
    desired_capacity = asg_response.get("AutoScalingGroups")[0].get("DesiredCapacity")
    instance_id = asg_response.get("AutoScalingGroups")[0].get("Instances")[0].get("InstanceId")
    
    ec2_response = ec2_client.describe_instances(
    InstanceIds=[instance_id]
    )
    cpu_cores = ec2_response.get("Reservations")[0].get("Instances")[0].get("CpuOptions").get("CoreCount")
    print(ec2_response)
    containers_by_cpu = int(cpu_cores//cpu_cores_assigned_to_containers)
    print(ec2_response.get("Reservations")[0].get("Instances")[0].get("InstanceType"))
    print(containers_by_cpu)

# def get_cluster_instances(ecs_client):
#     response = ecs_client.list_container_instances(
#     cluster = cluster_name,
#     status = 'ACTIVE'
#     )
#     instance_arns = response.get("containerInstanceArns")
#     ec2_client = get_ec2_client()
#     get_instance_details(ec2_client,instance_arns[0])
#     # number_of_instances = len(response.get("containerInstanceArns"))
#     #print("****************")
#     #print(number_of_instances)
#     # print(instance_arns)

def main():
    asg_client = get_asg_client()
    ec2_client = get_ec2_client()
    asg_name = get_asg_name(asg_client)
    describe_asg(asg_client, ec2_client, asg_name)

if __name__ == "__main__":
    main()