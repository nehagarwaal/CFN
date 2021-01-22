import boto3

def get_s3_client():
    client = boto3.client('s3control')
    return client

def get_s3_bucket_access(s3control_client):
    response = s3control_client.get_public_access_block(
    AccountId = str(346319152574)
    )
    print(response)
    
def main():
    s3control_client = get_s3_client()
    get_s3_bucket_access(s3control_client)

if __name__ == "__main__":
    main()