Issues in EKS Fargate:
S.No.	Issues	Findings	Resolutions	Status
1.	
Consul connectivity using EC2 tags

Consul agent uses EC2 instance's metadata to fetch IAM role profile and use it to fetch consul servers using EC2 tags
This works with IAM Users (Access & Secret Key) but not with IAM Roles (STS Token)
As a temporary fix, we are fetching consul servers' IP using DNS.

Open
2.	
Application logs through Kinesis Firehose

The current AWS SDK used in applications, does not support using Kinesis in EKS Fargate
Updating AWS SDK versions in platform common code

Closed
3.	
Pod restarts (Unavailable pods)

Liveness healthcheck should not be equal to Readiness healthcheck 
Unnecessary network calls also impact CPU Utilization of the application
Having 2 healthchecks in each application.

Lightweight: Returns 200 OK
Heavy: Makes network calls to check dependent applications

Closed
4.	
Resource unavailable (503 in application logs)

On heavy load, applications throw 503 error
Received timeouts in telnet and nslookup 
Changed the size of CoreDNS pods and configured HPA which resolved 503 exceptions
But requires more pods of CoreDNS on high load
Closed
Performance Test results:
Current Load on production: 1 RPS

S.No.	Applications	Load	Findings	Kibana	Grafana
1.	Flights Engine, USG and Travelport connector	4 RPS	
Performance was as expected
Lesser number of pods
No Unavailable pods
No latency
Logs	Infra

Application
2.	Flights Engine, USG and Travelport connector	10 RPS	
Performance broke after 5.5 rps
(Need to work on TP right pod sizing)
More than 10 CoreDNS pods needed
Logs	
Infra

Application

Cost Calculation:
Resources requested	EC2 (per month)	EKS Fargate (per month)	EKS Fargate Savings Plan
CPU cores = 2vCPU
Memory = 4GB
Pod Count = 12	
Instance type = c5.4xlarge * 2 (8 pods per instance)

100% On-demand = $995.52
100% RI = $343.10
100% Spot = $439.344
CPU = $0.04048 per core per hour

(0.04048*32*24*30 = $699.49)

Memory =$0.004445 per GB per hour

(0.004445*4*12*24*30 = $153.6192)

Total = $853.10

CPU = $0.03036 per core per hour

Memory =$0.00333375 per GB per hour

Detailed analysis:
Cost
Performance Tests
