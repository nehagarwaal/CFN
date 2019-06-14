import boto3

def get_ssm_client():
        try:
            ssm_client = boto3.client("ssm")
            return ssm_client
        except:
            print("Access denied, check permissions")

def put_complaince_status_to_parameterstore(ssm_client, s3_bucket_name, bucket_compliance):
        ssm_client.put_parameter(
            Name="s3_public_compliance_" + s3_bucket_name,
            Value=((str(bucket_compliance).replace('[', '')).replace(']', '')).replace(' ', ''),
            Type='String',
            Overwrite=True
        )

def main():
    bucket_compliance = [True, False]
    ssm_client = get_ssm_client()
    put_complaince_status_to_parameterstore(ssm_client, "test-private-test", bucket_compliance)

if __name__ == "__main__":
    main()
