
Areas	EKS Managed	EKS Fargate
COMPUTE
One cluster to manage both	Yes

Extra configuration for Fargate in the cluster control plane	N/A	EKS Fargate Profile, EKS Fargate Pod Execution Role
Pod Login	Yes	Yes
Underlying instance metadata call	Yes	No: Changes required for Consul connectivity
(Container meta data call is available in ECS)
Manage auto scaling of worker nodes	
Requires various updates in worker nodes such as k8s version, 7 day patching, TMDS agent
Components required to be managed:

K8s Cluster autoscaler (worker nodes scaleups and scaledowns)
4 ASGs
4 Launch Templares
No Management of worker nodes. 

Load Balancers	Exposed as service: Classic and Network Load balancers. 
Supports ALB Ingress (ALB and NLB).	Does not support exposing deployment as load balancer service.
Supports ALB Ingress (ALB and NLB).
Kubelet	Runs in every worker node	Runs as a sidecard container inside each Fargate pod and reserves 256 MB of RAM.
NETWORK
Security groups for pods	Yes	No
Pods network	Public and private subnets	Private subnets
 VPC secondary CIDR blocks	Yes	Yes
Specify Host port and Host Network	Yes	No
COST
EKS Cluster	$0.10 per hour	$0.10 per hour
Compute cost (16 cores 32 GB)	
ALB
EC2 instances and EBS volumes
ALB
vCPU and memory resources used
($0.68 c5.4xlarge + cost of volumes) per hour	$0.78992 per hour

per vCPU per hour = $0.04048
per GB per hour = $0.004445
SECURITY
PCI-DSS Compliant	Yes	TO BE UPDATED
LOGGING & MONITORING
Cloudwatch Container Insights	Yes	Yes
Prometheus	Yes	Yes (requires Prometheus to be deployed separately on EC2 boxes)
Kubernetes Service account support 	
Python (Boto3) — 1.9.220

Python (botocore) — 1.12.200

.NET — 3.3.659.1
AWS CLI — 1.16.232
Python (Boto3) — 1.9.220

Python (botocore) — 1.12.200

.NET — 3.3.659.1
AWS CLI — 1.16.232


Other findings:

ALB Ingress controller
- If we use ALB Ingress controller (internet facing and internal available), we do not need to add a separate load balancer to expose any deployment.
   It will initiate a new ALB for the ingress rule managed by ingress controller.
- OIDC setup is required for ALB Ingress
- No new ALB is created for one ingress: One ALB ingress can manage multiple k8s services
- Pods are directly registered as targets instead of worker nodes

Consul connectivity- Since we cannot make a metadata call for fargate worker nodes, we need to think ofsome other alternative
Solution: 
- Update python script to fetch private IP of the pod instead of EC2 instance
- Use consul endpoint instead of fetching instances by tag names
AWS Fargate Spot: Available for Fargate ECS
With Fargate savings plans offers savings of up to 50% on your AWS Fargate usage
