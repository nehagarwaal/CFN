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

Account=$ApplicationAccount-$Environment
AccountIDParam=$Account-id
AccountID=`aws ssm get-parameter --name $AccountIDParam --with-decryption --region $Region | jq .Parameter.Value`
AccountID=${AccountID:1:-1}

role="arn:aws:iam::$AccountID:role/deployment-role"

aws sts assume-role --role-arn $role --role-session-name TemporarySessionKeys --output json > assume-role-output.json
AWS_ACCESS_KEY_ID=$(jq .Credentials.AccessKeyId assume-role-output.json)

AWS_SECRET_ACCESS_KEY=$(jq .Credentials.SecretAccessKey assume-role-output.json)

AWS_SESSION_TOKEN=$(jq .Credentials.SessionToken assume-role-output.json)


export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:1:-1}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:1:-1}"
export AWS_SESSION_TOKEN="${AWS_SESSION_TOKEN:1:-1}"


stackName=$Product"-"$ApplicationName"-Skeleton"
echo $stackName
if [[ $Operation == "create" ]]
then 
	aws cloudformation delete-stack --stack-name $stackName --region $Region
else
	aws cloudformation cancel-update-stack --stack-name $stackName --region $Region
fi

unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
unset AWS_SESSION_TOKEN
