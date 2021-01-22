import boto3

cidr_to_delete = "1.2.3.4"
cidr_to_match = "1.2.3.4"
vpc_id_to_filter = "vpc-abcd"

ec2_client = boto3.client("ec2")

def filter_security_groups(filter_condition):
    list_of_matching_security_groups = []
    security_groups_to_be_modified = []
    response = ec2_client.describe_security_groups(
        Filters=[
        {
            'Name': filter_condition,
            'Values': [
                cidr_to_match
            ]
        },
        {
            'Name': 'vpc-id',
            'Values': [
                vpc_id_to_filter
            ]
        }
        ]   
    )
    for sg in response.get("SecurityGroups"):
        for ip_permission in sg.get("IpPermissions"):
            for ip_range in ip_permission.get("IpRanges"):
                if ip_range.get("CidrIp") == cidr_to_match:
                    rule = {
                        "sgid": sg.get("GroupId"),
                        "fromport": ip_permission.get("FromPort"),
                        "toport": ip_permission.get("ToPort"),
                        "ipprotocol": ip_permission.get("IpProtocol")
                    }
                    security_groups_to_be_modified.append(sg.get("GroupId"))
                    list_of_matching_security_groups.append(rule)
    print("Security groups to be modified are " + str(len(set(security_groups_to_be_modified))))
    print(set(security_groups_to_be_modified))
    return list_of_matching_security_groups   

def modify_security_groups(ingress_rules_to_be_modified, egress_rules_to_be_modified):
    for rule in ingress_rules_to_be_modified:
        try:
            if rule.get("fromport") == None and rule.get("toport") == None:
                ec2_client.revoke_security_group_ingress(
                    CidrIp=cidr_to_delete,
                    GroupId=rule.get("sgid"),
                    IpProtocol=rule.get("ipprotocol")
                ) 
                print("Ingress removed from " + rule.get("sgid"))  
            elif (rule.get("fromport") != None and rule.get("toport") != None):
                ec2_client.revoke_security_group_ingress(
                    CidrIp=cidr_to_delete,
                    GroupId=rule.get("sgid"),
                    FromPort=rule.get("fromport"),
                    ToPort=rule.get("toport"),
                    IpProtocol=rule.get("ipprotocol")
                )
                print("Ingress removed from " + rule.get("sgid"))                
        except:
            print("Failed to delete this rule" + str(rule))
            raise

    for rule in egress_rules_to_be_modified:
        try:
            if rule.get("fromport") != "None" and rule.get("toport") != "None":
                ec2_client.revoke_security_group_egress(
                    CidrIp=cidr_to_delete,
                    GroupId=rule.get("sgid"),
                    FromPort=rule.get("fromport"),
                    ToPort=rule.get("toport"),
                    IpProtocol=rule.get("ipprotocol")
                )
                print("Egress removed from " + rule.get("sgid"))  
            elif rule.get("fromport") == "None" and rule.get("toport") == "None":
                ec2_client.revoke_security_group_ingress(
                    CidrIp=cidr_to_delete,
                    GroupId=rule.get("sgid"),
                    IpProtocol=rule.get("ipprotocol")
                ) 
                print("Egresss removed from " + rule.get("sgid"))                
        except:
            print("Failed to delete this rule" + rule)
            raise

def main():
    ingress_rules_to_be_modified = filter_security_groups("ip-permission.cidr")
    print("Ingress rules to be modified are " + str(len(ingress_rules_to_be_modified)))
    print(ingress_rules_to_be_modified)

    egress_rules_to_be_modified = filter_security_groups("egress.ip-permission.cidr")
    print("Egress rules to be modified are " + str(len(egress_rules_to_be_modified)))
    print(egress_rules_to_be_modified)    

    # modify_security_groups(ingress_rules_to_be_modified, egress_rules_to_be_modified)

if __name__ == "__main__":
    main()