# Amazon ECS Cluster autoscaling

Problem :

A limitation of CloudWatch alarm is that it allows you to choose only one metric at a time. It’s possible to set up two different alarms (one for CPU and one for memory) and trigger the AutoScaling Group to scale out. But when both metrics are used to scale in, you run into troubles. Imagine when you have high CPU but low memory reservation. One alarm tries to scale out while the other wants to scale in. You end up in a situation where a new container instance is launched and another terminated again and again.

This gets even worse because tasks are not re-scheduled when a new container instance gets launched. But when AutoScaling group terminates an instance, it normally chooses the oldest one (usually with many tasks running). That makes the cluster unstable as the tasks need to be scheduled over and over again.

Solution:

To solve the above issue, we are in a dire need to have a # Custom CloudWatch metric that will count the maximum number of largest containers that can be accomodated per instance in the ECS Cluster. To get a better performance of the application, we will try to keep a space of atleast 2 conatiners to scale up at any point of time. This allows for faster scale-up as the instance is ready whenever container needs to scale-up. So far scale sounds good. 

How about when traffic reduces and you want to scale down the cluster?

For that we will trigger a scale down CloudWatch alarm that will make sure to keep atleast a sapce of 2 conatiners to scale up.

Infrastructure of the solution:
