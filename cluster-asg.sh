#!/bin/bash

set -e

POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    --product)
    Product="$2"
    shift # past argument
    shift # past value
    ;;
    --app-name)
    ApplicationName="$2"
    shift # past argument
    shift # past value
    ;;
    --environment)
    Environment="$2"
    shift # past argument
    shift # past value
    ;;
	--app-account)
    ApplicationAccount="$2"
    shift # past argument
    shift # past value
    ;;
	--amiid)
    AMIID="$2"
    shift # past argument
    shift # past value
    ;;
	--desired-capacity)
    DesiredCapacity="$2"
    shift # past argument
    shift # past value
    ;;
	--max-capacity)
    MaxCapacity="$2"
    shift # past argument
    shift # past value
	;;
	--min-capacity)
    MinCapacity="$2"
    shift # past argument
    shift # past value
	;;
	--instance-type)
    InstanceType="$2"
    shift # past argument
    shift # past value
	;;
	--common-ec2-sg)
	if [[ $2 == --* ]]; then
		shift
	else
		CommonEC2SecurityGroup="$2"
		shift # past argument
		shift # past value
	fi
	;;
	--ec2-subnet)
    EC2Subnet="$2"
    shift # past argument
    shift # past value
	;;
	--product-owner-email)
    ProductOwnerEmail="$2"
    shift # past argument
    shift # past value
	;;
	--app-owner-email)
    ApplicationOwnerEmail="$2"
    shift # past argument
    shift # past value
	;;
	--purpose)
    Purpose="$2"
    shift # past argument
    shift # past value
	;;
	--alert-logic-appliance-ip)
	if [[ $2 == --* ]]; then
		shift
	else
		AlertLogicApplianceIp="$2"
		shift # past argument
		shift # past value
	fi
	;;
	--instance-profile)
	if [[ $2 == --* ]]; then
		shift
	else
		IAMInstanceProfileRole="$2"
		shift # past argument
		shift # past value
	fi
	;;
	--operation)
    Operation="$2"
    shift # past argument
    shift # past value
	;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

echo Product = "${Product}"
echo Application Name = "${ApplicationName}"
echo Environment = "${Environment}"
echo Application Account = "${ApplicationAccount}"
echo AMIID = "${AMIID}"
echo Desired Capacity = "${DesiredCapacity}"
echo Maximum Capacity = "${MaxCapacity}"
echo Desired Capacity = "${DesiredCapacity}"
echo Minimum Capacity = "${MinCapacity}"
echo Instance Type = "${InstanceType}"
echo Common EC2 SG = "${CommonEC2SecurityGroup}"
echo EC2 Subnets = "${EC2Subnet}"
echo Product Owner = "${ProductOwnerEmail}"
echo Application Owner = "${ApplicationOwnerEmail}"
echo Purpose = "${Purpose}"
echo Alert Logic IP = "${AlertLogicApplianceIp}"
echo Instance Profile = "${IAMInstanceProfileRole}"
echo Operation = "${Operation}"

#Change WORKSPACE permissions
Region="us-east-1"
curPath=`pwd`

stackName=$Product"-"$ApplicationName"-ASG-"${InstanceType//.}

templatePath="file://"$curPath"/ecs/cluster-test/cf-templates/cluster-asg.json"
parametersPath="file://"$curPath"/ecs/cluster-test/cf-templates/parameters-asg.json"

#Get account ID from common account parameter store
Account=$ApplicationAccount-$Environment
AccountIDParam=$Account-id
AccountID=`aws ssm get-parameter --name $AccountIDParam --with-decryption --region $Region | jq .Parameter.Value`

AccountID=${AccountID:1:-1}

if [ $ApplicationAccount == "pci" ]; then
	case "$Environment" in 
		qa) 
			Domain="qa.secure.cnxloyalty.com"
		;;
		stage)
			Domain="stage.secure.cnxloyalty.com"
		;;
		prod)
			Domain="secure.cnxloyalty.com"
		;;
		*)
		;;
	esac
else
	case "$Environment" in 
		qa) 
			Domain="qa.cnxloyalty.com"
		;;
		stage)
			Domain="stage.cnxloyalty.com"
		;;
		prod)
			Domain="cnxloyalty.com"
		;;
		*)
	esac
fi

role="arn:aws:iam::$AccountID:role/deployment-role"
aws sts assume-role --role-arn $role --role-session-name TemporarySessionKeys --output json > assume-role-output.json
AWS_ACCESS_KEY_ID=$(jq .Credentials.AccessKeyId assume-role-output.json)

AWS_SECRET_ACCESS_KEY=$(jq .Credentials.SecretAccessKey assume-role-output.json)

AWS_SESSION_TOKEN=$(jq .Credentials.SessionToken assume-role-output.json)


export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:1:-1}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:1:-1}"
export AWS_SESSION_TOKEN="${AWS_SESSION_TOKEN:1:-1}"

#finding the VpcId
aws ec2 describe-vpcs --filter Name=tag:Name,Values=$Account --region $Region > temp.json
VpcId=$(jq '.Vpcs[].VpcId' temp.json)
echo $VpcId

VpcId="${VpcId:1:-1}"
echo $VpcId

#FindingAppSubnets
aws ec2 describe-subnets --filters Name=tag:Name,Values=$Account-app-* --region $Region> temp.json
jq '.Subnets[].SubnetId' temp.json > temp1.json 
tr '"' ' ' < temp1.json > temp.json
sed ':a;N;$!ba;s/\n/,/g' temp.json > temp1.json
appsubnets=`sed 's/ //g' temp1.json`
echo $appsubnets

#FindingWebSubnets
aws ec2 describe-subnets --filters Name=tag:Name,Values=$Account-web-* --region $Region> temp.json
jq '.Subnets[].SubnetId' temp.json > temp1.json
tr '"' ' ' < temp1.json > temp.json
sed ':a;N;$!ba;s/\n/,/g' temp.json > temp1.json
websubnets=`sed 's/ //g' temp1.json`
echo $websubnets

SNSTopicARN="arn:aws:sns:us-east-1:$AccountID:Autoscaling-Notification"
IAMRoleARN="arn:aws:iam::$AccountID:role/SNSLambdaRole"

cd ./ecs/cluster-test/cf-templates

sed -i -- 's/key_name/'${Account}'/g' "./parameters-asg.json"

sed -i -- 's/ami_id/'${AMIID}'/g' "./parameters-asg.json"
sed -i -- 's/vpc_id/'${VpcId}'/g' "./parameters-asg.json"
sed -i -- 's/desired_capacity/'${DesiredCapacity}'/g' "./parameters-asg.json"
sed -i -- 's/max_capacity/'${MaxCapacity}'/g' "./parameters-asg.json"
sed -i -- 's/min_capacity/'${MinCapacity}'/g' "./parameters-asg.json"
sed -i -- 's/instance_type/'${InstanceType}'/g' "./parameters-asg.json"
sed -i -- 's/Ec2_common-security_groups/'${CommonEC2SecurityGroup}'/g' "./parameters-asg.json"
sed -i -- 's/product/'${Product}'/g' "./parameters-asg.json"
sed -i -- 's/app_name/'${ApplicationName}'/g' "./parameters-asg.json"
sed -i -- 's/application_subnets/'${appsubnets}'/g' "./parameters-asg.json"
sed -i -- 's/web_subnets/'${websubnets}'/g' "./parameters-asg.json"
sed -i -- 's/EC2_Subnet/'${EC2Subnet}'/g' "./parameters-asg.json"
sed -i -- 's/environment/'${ApplicationAccount}-${Environment}'/g' "./parameters-asg.json"
sed -i -- 's/region/'${Region}'/g' "./parameters-asg.json"
sed -i -- 's/Products_owner_email/'${ProductOwnerEmail}'/g' "./parameters-asg.json"
sed -i -- 's/application_owner_email/'${ApplicationOwnerEmail}'/g' "./parameters-asg.json"
sed -i -- 's/purpose/'${Purpose}'/g' "./parameters-asg.json"
sed -i -- 's/al_appliance_host_ip/'${AlertLogicApplianceIp}'/g' "./parameters-asg.json"
sed -i -- 's/iam_instance_role/'${IAMInstanceProfileRole}'/g' "./parameters-asg.json"
sed -i -- 's~certificate_arn~'${CertificateARN}'~g' "./parameters-asg.json"
sed -i -- 's~sns_topic_arn~'${SNSTopicARN}'~g' "./parameters-asg.json"
sed -i -- 's~iam_role_arn~'${IAMRoleARN}'~g' "./parameters-asg.json"

cat "./parameters-asg.json"

aws cloudformation $Operation-stack --stack-name $stackName  --region $Region  --template-body $templatePath --parameters $parametersPath --capabilities CAPABILITY_IAM

aws cloudformation wait stack-$Operation-complete --stack-name $stackName --region $Region 

unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
unset AWS_SESSION_TOKEN
