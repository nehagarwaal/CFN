import boto3
import os

cidr_to_add = str(os.environ["cidr_to_add"])
existing_ips_to_match  = str(os.environ["existing_ips_to_match"])

def get_waf_client():
    client = boto3.client("waf-regional")
    return client

def get_change_token(waf_client):
    change_token = waf_client.get_change_token()
    return change_token.get("ChangeToken")

def get_ip_conditions_to_modify(waf_client):
    try:
        waf_ip_sets_to_modify = []
        response = waf_client.list_ip_sets()
        ip_set_list = response.get("IPSets")
        for ip_set in ip_set_list:
            response = waf_client.get_ip_set(
                IPSetId=ip_set["IPSetId"]
            )
            for ip in response.get("IPSet").get("IPSetDescriptors"):
                if ip.get("Value") in existing_ips_to_match:
                    waf_ip_sets_to_modify.append(ip_set)
                    break
        print('**WAF IP Conditions to modify are** \n' + waf_ip_sets_to_modify)
        return waf_ip_sets_to_modify
    
    except:
        print ("Falied to fetch IP conditions to be modified")
        raise 

def add_cidr_ip_conditions(waf_client, waf_ip_sets_to_modify):
    try:
        change_token = get_change_token(waf_client)
        for ip_set in waf_ip_sets_to_modify:
            waf_client.update_ip_set(
                IPSetId=ip_set["IPSetId"],
                ChangeToken=change_token,
                Updates=[
                    {
                        'Action': 'INSERT',
                        'IPSetDescriptor': {
                            'Type': 'IPV4',
                            'Value': cidr_to_add
                        }
                    }
                ]
            )
            print("Added in " + ip_set["Name"])
    
    except:
        print ("Falied to update IP conditions")
        raise 

def lambda_handler(event, context):
    waf_client = get_waf_client()
    waf_ip_sets_to_modify = get_ip_conditions_to_modify(waf_client)
    add_cidr_ip_conditions(waf_client,waf_ip_sets_to_modify)
