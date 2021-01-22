import boto3

# def check_bucket_name_in_public_bucket_list():
#     s3_resource = boto3.resource('s3')
#     bucket = s3_resource.Bucket('cnx-nextgen-devops')

#Entry point
def main(): 
      client = boto3.client('s3')
#     response = client.get_bucket_policy_status(Bucket='test-private-test')
      
#     print(response)
#       check_bucket_name_in_public_bucket_list()

if __name__ == "__main__":
        main()