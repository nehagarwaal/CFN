import boto3

def get_sns_client():
    sns_client = boto3.client('sns')
    return sns_client

def publish_msg_to_sns(sns_client):
    s3_bucket_name = "test-private-test"
    response = sns_client.publish(
        TopicArn='arn',
        Message='S3 bucket "' + s3_bucket_name + '" was made public on p-qa account. It has been made private.',
        Subject='Revoked public S3 Bucket',
        MessageStructure='testfromscript'
    )

def main():
    sns_client = get_sns_client()
    publish_msg_to_sns(sns_client)

if __name__ == "__main__":
    main()
