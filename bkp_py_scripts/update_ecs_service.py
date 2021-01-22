import boto3

cluster_name = "Flights-Connector"
service_name = "Connector-Travelport"

def get_ecs_client():
    client = boto3.client('ecs')
    return client

def describe_ecs_service(ecs_client):
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

def update_ecs_service(ecs_client,new_desired_count):
    response = ecs_client.update_service(
        cluster=cluster_name,
        service=service_name,
        desiredCount=new_desired_count,
        taskDefinition=task_definition,
        deploymentConfiguration={
            'maximumPercent': 200,
            'minimumHealthyPercent': 100
        },
        forceNewDeployment=True,
        healthCheckGracePeriodSeconds=0
    )   
    print(response)


def main():
    ecs_client = get_ecs_client()
    desired_count = describe_ecs_service(ecs_client)
    if desired_count >= 8:
        new_desired_count = 8
    elif desired_count < 8:
        new_desired_count = desired_count
    update_ecs_service(ecs_client,new_desired_count)

if __name__ == "__main__":
    main()

