# Amazon ECS Cluster autoscaling

**Problem :**

Amazon provides various metrics to scale instances in ASG. For scaling ECS Cluster, we can consider the following two metrics:

- CPUReservation
- MemoryReservation
Regardless of these two metrics, ECS Cluster will always be in a state of dilemma of > **whether to scale itself on CPUReservation or MemoryReservation.**

It’s possible to set up two different alarms (one for CPU and one for memory) and trigger the AutoScaling Group to scale out. But when both metrics are used to scale in, you run into troubles. Imagine when you have high CPU but low memory reservation. One alarm tries to scale out while the other wants to scale in. You end up in a situation where a new container instance is launched and another terminated again and again.

This gets even worse because tasks are not re-scheduled when a new container instance gets launched. But when AutoScaling group terminates an instance, it normally chooses the oldest one (usually with many tasks running). That makes the cluster unstable as the tasks need to be scheduled over and over again.

**Solution:**

To solve the above issue, we are in a dire need to have a # Custom CloudWatch metric that will count the maximum number of largest containers that can be accomodated per instance in the ECS Cluster. To get a better performance of the application, we will try to keep a space of atleast 2 conatiners to scale up at any point of time. This allows for faster scale-up as the instance is ready whenever container needs to scale-up. So far scale sounds good. 

How about when traffic reduces and you want to scale down the cluster?

For that we will trigger a scale down CloudWatch alarm that will make sure to keep atleast a sapce of 2 conatiners to scale up.

**Infrastructure of the solution:**

https://github.com/nehagarwaal/Scripts/blob/python/ECS_Cluster_Scaling_Infra.PNG

**Lambda function algorithm:**

1. Obtain the total number of instances in the ECS Cluster whose ECS Agent is Connected
2. Fetch the remaining CPU and Memory in each instance
3. For each instance, calculate the number of largest containers that can be placed with the below mentioned logic:

> containers_by_cpu =int(remaining_cpu//cpu_cores_assigned_to_containers)
> containers_by_memory =int(remaining_memory//soft_limit_of_container)
> container_capacity_per_instance =min(containers_by_cpu,containers_by_memory)

This will return an array of container capacity per instance.

4. Find the sum of this array to calculate the total number of largest containers that can be placed in the cluster
5. Finally, create a CloudWatch event to push this metric every minute to CloudWatch Metrics

The next step is to set up two CloudWatch Alarms to scale up and scale down the ECS Cluster as per thresholds set on this metric.

**Key points to keep in mind:**

3 parameters to run this lambda function: cluster_name, container_cpu_cores, container_soft_limit
Alarm thresholds will change as per the instance type

**Fallback Strategy:**

CloudWatch alarm on Error count of the Lambda Function.
