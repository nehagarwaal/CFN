import boto3
import json

s3_bucket_name = "test-private-test"
statements_to_delete = []
statements_in_bucket_policy = []

def get_s3_client():
    client = boto3.client("s3")
    return client
 
def update_s3_bucket_policy(s3_client):
    response = (s3_client.get_bucket_policy(Bucket=s3_bucket_name)).get("Policy")
    bucket_policy = json.loads(str(response))
    for statement in bucket_policy.get("Statement"):
        if statement.get("Principal") == '*':
            statements_to_delete.append(statement)  
    if len(statements_to_delete) == len(bucket_policy.get("Statement")):
        s3_client.delete_bucket_policy(Bucket=s3_bucket_name)
    else:
        i = 0
        statements_in_bucket_policy = bucket_policy.get("Statement")
        for statement1 in statements_in_bucket_policy:
            for statement2 in statements_to_delete:
                if statement2 == statement1:
                    statements_in_bucket_policy.pop(i)
                else:
                    i = i+1
        print(statements_in_bucket_policy)
        updated_bucket_policy = {
            "Version": "2012-10-17",
            "Statement": statements_in_bucket_policy 
            }
        updated_bucket_policy_json = json.dumps(updated_bucket_policy)
        s3_client.put_bucket_policy(
            Bucket=s3_bucket_name,
            Policy=updated_bucket_policy_json
        )
        
def main():
        s3_client = get_s3_client()
        update_s3_bucket_policy(s3_client)
        
if __name__ == "__main__":
        main()