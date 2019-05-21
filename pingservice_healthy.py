import urllib
import boto3
import os
import sys

urls = str(os.environ["urls"]).split(",")

def get_cloudwatch_client():
    client = boto3.client("cloudwatch")
    return client

def get_response_codes():
    cloudwatch_data = []
    i = 0
    for url in urls:
        service_name = urls[i].split("-" , 2)[1].split(".", 2)[0]
        try:
            response_code = urllib.request.urlopen(url).getcode()
        except urllib.error.HTTPError as error_code:
            response_code = error_code.code
            pass
        data = get_metric_data_structure(response_code, service_name)
        cloudwatch_data.append(data)
        i = i + 1
        print(url)
        print(response_code)
    return cloudwatch_data

def get_metric_data_structure(response_code, service_name):
    data = {
        "MetricName" : 'Response_Status_Codes',
        "Value" : response_code,
        "Unit" : "None",
        "Dimensions": [
                {
                    "Name": "Service_Names",
                    "Value": service_name
                }
            ]
    }
    return data

def put_metrics_to_cloudwatch(cw_client,cloudwatch_data):
   try:
        for data in cloudwatch_data:
            cw_client.put_metric_data(
                Namespace = "Flights_PingService_Response",
                MetricData=[data]
             )
   except:
        print(sys.exc_info)
        pass

def lambda_handler(event, context):
    cw_client = get_cloudwatch_client()
    service_metric_dictionary = get_response_codes()
    print(service_metric_dictionary)
    put_metrics_to_cloudwatch(cw_client,service_metric_dictionary)
