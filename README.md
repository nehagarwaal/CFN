# nextgen-air-infrastructure
Repository for Nextgen Air Infrastructure Codebase

The current infrastructure includes single cloudformation script that deploys following major components:
1. Application Load Balancer
2. Listener Rule
3. Default Target Group
4. ECS Cluster
5. Launch Configuration
6. Auto scaling group
7. Security Groups

The difficulty anyone can face here is when they want to deploy multiple services in different instance types in a single cluster behind a single ALB. To suffice this, they are only left with the option of deploying multiple ECS clusters.

### How about deploying multiple instance types in the same cluster?

To implement this, we have riven the existing CFN into two parts:

The first CFN will deploy the following resources:
1. Application Load Balancer
2. Listener Rule
3. Default Target Group
4. ECS Cluster with no instances

The second CFN will deploy the following resources:
1. Launch Configuration
2. Auto scaling group
3. Security Groups
4. Shell script to join the newly created ASG to an existing ECS Cluster [df1]

> `NOTE: CFN-2 does not depend on CFN-1. It can be used with existing ECS cluster.`

Now, let us consider an example where we want to deploy Travelport connector in m3.medium and Sabre connector in c4.large instance type. In order to do this, we can run the second CFN twice to deploy two different ASGs in the cluster and run the updated service deployment CFN which has additional property of `Task Placement Constraints`.

This Task Placement Constraint will enforce the service to get deployed in the desired instance type.
