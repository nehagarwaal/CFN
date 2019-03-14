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
	--common-alb-sg)
	if [[ $2 == --* ]]; then
		shift
	else
		CommonALBSecurityGroup="$2"
		shift # past argument
		shift # past value
	fi
	;;
	--alb-subnet)
    ALBSubnet="$2"
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
echo Common ALB SG = "${CommonALBSecurityGroup}"
echo ALB Subnets = "${ALBSubnet}"
echo Product Owner = "${ProductOwnerEmail}"
echo Application Owner = "${ApplicationOwnerEmail}"
echo Purpose = "${Purpose}"
echo Operation = "${Operation}"

#Change WORKSPACE permissions
Region="us-east-1"
curPath=`pwd`

stackName=$Product"-"$ApplicationName"-Skeleton"

templatePath="file://"$curPath"/ecs/cluster-test/cf-templates/cluster.json"
parametersPath="file://"$curPath"/ecs/cluster-test/cf-templates/parameters.json"

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

#Get Certificate ARN from domain name
CertificateARN=`aws acm list-certificates --region $Region --output text | grep $Domain | awk -F " " '{print $2}'`
if [[ $CertificateARN != arn* ]]; then
exit 1
fi

#finding the VpcId
aws ec2 describe-vpcs --filter Name=tag:Name,Values=$Account --region $Region > temp.json
VpcId=$(jq '.Vpcs[].VpcId' temp.json)
echo $VpcId

VpcId="${VpcId:1:-1}"
echo $VpcId

#FindingWebSubnets
aws ec2 describe-subnets --filters Name=tag:Name,Values=$Account-web-* --region $Region> temp.json
jq '.Subnets[].SubnetId' temp.json > temp1.json
tr '"' ' ' < temp1.json > temp.json
sed ':a;N;$!ba;s/\n/,/g' temp.json > temp1.json
websubnets=`sed 's/ //g' temp1.json`
echo $websubnets

#FindingPublicSubnets
aws ec2 describe-subnets --filters Name=tag:Name,Values=$Account-public-* --region $Region> temp.json
jq '.Subnets[].SubnetId' temp.json > temp1.json
tr '"' ' ' < temp1.json > temp.json
sed ':a;N;$!ba;s/\n/,/g' temp.json > temp1.json 
publicsubnets=`sed 's/ //g' temp1.json`
echo $publicsubnets

SNSTopicARN="arn:aws:sns:us-east-1:$AccountID:Autoscaling-Notification"
IAMRoleARN="arn:aws:iam::$AccountID:role/SNSLambdaRole"

cd ./ecs/cluster-test/cf-templates

sed -i -- 's/key_name/'${Account}'/g' "./parameters.json"

sed -i -- 's/vpc_id/'${VpcId}'/g' "./parameters.json"
sed -i -- 's/Alb_common-security_groups/'${CommonALBSecurityGroup}'/g' "./parameters.json"
sed -i -- 's/product/'${Product}'/g' "./parameters.json"
sed -i -- 's/app_name/'${ApplicationName}'/g' "./parameters.json"
sed -i -- 's/public_subnets/'${publicsubnets}'/g' "./parameters.json"
sed -i -- 's/web_subnets/'${websubnets}'/g' "./parameters.json"
sed -i -- 's/Alb_Subnet/'${ALBSubnet}'/g' "./parameters.json"
sed -i -- 's/environment/'${ApplicationAccount}-${Environment}'/g' "./parameters.json"
sed -i -- 's/region/'${Region}'/g' "./parameters.json"
sed -i -- 's/Products_owner_email/'${ProductOwnerEmail}'/g' "./parameters.json"
sed -i -- 's/application_owner_email/'${ApplicationOwnerEmail}'/g' "./parameters.json"
sed -i -- 's/purpose/'${Purpose}'/g' "./parameters.json"
sed -i -- 's~certificate_arn~'${CertificateARN}'~g' "./parameters.json"
sed -i -- 's~sns_topic_arn~'${SNSTopicARN}'~g' "./parameters.json"
sed -i -- 's~iam_role_arn~'${IAMRoleARN}'~g' "./parameters.json"

cat "./parameters.json"

aws cloudformation $Operation-stack --stack-name $stackName  --region $Region  --template-body $templatePath --parameters $parametersPath --capabilities CAPABILITY_IAM

aws cloudformation wait stack-$Operation-complete --stack-name $stackName --region $Region 

unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
unset AWS_SESSION_TOKEN

