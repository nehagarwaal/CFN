import boto3
import datetime
import dateutil

def get_ec2_client():
    client = boto3.client("ec2")
    return client

def describe_snapshots(ec2_client):
    timeLimit=datetime.datetime.now() - datetime.timedelta(days=200)

    print(timeLimit)
    response = ec2_client.describe_snapshots(
        Filters=[
            {
                'Name': 'start-time',
                'Values': [
                    timeLimit
                ]
            }
        ]
    )
    print(response)

def main():
    ec2_client = get_ec2_client()
    describe_snapshots(ec2_client)

if __name__ == "__main__":
    main()