import boto3

list_of_uris = [ "" ]

rule_name = "abc"
condition_name = "abc"

def get_waf_client():
    client = boto3.client("waf-regional")
    return client

def get_change_token(waf_client):
    change_token = waf_client.get_change_token()
    return change_token.get("ChangeToken")

def create_uri_condition(waf_client):
    change_token = get_change_token(waf_client)
    response = waf_client.create_byte_match_set(
    Name=condition_name,
    ChangeToken=change_token
    )
    condition_id = response.get("ByteMatchSet").get("ByteMatchSetId")
    return condition_id

def update_uri_condition(waf_client, condition_id):
    for uri in list_of_uris:
        change_token = get_change_token(waf_client)
        waf_client.update_byte_match_set(
        ByteMatchSetId=condition_id,
        ChangeToken=change_token,
        Updates=[
            {
                'Action': 'INSERT',
                'ByteMatchTuple': {
                    'FieldToMatch': {
                        'Type': 'URI'
                    },
                    'TargetString': bytes(uri, encoding='utf-8'),
                    'TextTransformation': 'NONE',
                    'PositionalConstraint': 'STARTS_WITH'
                }
            }
        ]
        )

def create_rule(waf_client):
    change_token = get_change_token(waf_client)
    response = waf_client.create_rule(
    Name=rule_name,
    MetricName='abc',
    ChangeToken=change_token,
    Tags=[
        {
            'Key': 'Product',
            'Value': 'abc'
        },
        ]
    )
    rule_id = response.get("Rule").get("RuleId")
    print(rule_id)
    return rule_id

def update_rule(waf_client, rule_id, condition_id):
    change_token = get_change_token(waf_client)
    response = waf_client.update_rule(
        RuleId=rule_id,
        ChangeToken=change_token,
        Updates=[
            #URIs match
            {
                'Action': 'INSERT',
                'Predicate': {
                    'Negated': False,
                    'Type': 'ByteMatch',
                    'DataId': condition_id
                }
            },
            #IPs match
            {
                'Action': 'INSERT',
                'Predicate': {
                    'Negated': False,
                    'Type': 'IPMatch',
                    'DataId': "abc"
                }
            },
            #sql
            {
                'Action': 'INSERT',
                'Predicate': {
                    'Negated': True,
                    'Type': 'SqlInjectionMatch',
                    'DataId': "abc"
                }
            },
            #ccpa
            {
                'Action': 'INSERT',
                'Predicate': {
                    'Negated': True,
                    'Type': 'ByteMatch',
                    'DataId': "abc"
                }
            },
            #xss
            {
                'Action': 'INSERT',
                'Predicate': {
                    'Negated': True,
                    'Type': 'XssMatch',
                    'DataId': "abc"
                }
            }
        ]
    )

def main():
    waf_client = get_waf_client()
    condition_id = create_uri_condition(waf_client)
    update_uri_condition(waf_client, condition_id)
    rule_id = create_rule(waf_client)
    update_rule(waf_client, rule_id, condition_id)


if __name__ == "__main__":
    main()
