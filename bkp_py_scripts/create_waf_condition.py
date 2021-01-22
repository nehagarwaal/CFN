import boto3

list_of_uris = [
    "/api/air/v1.0/health", 
    "/api/air/v1.0/search",
    "/api/air/v1.0/facets",
    "/api/air/v1.0/price",
    "/api/air/v1.0/upsell",
    "/api/air/v1.0/book",
    "/api/air/v1.0/seatmap"
    ]

rule_name = "FlightsEngineRule-3"
condition_name = "Flights-Engine-URI-Conditions-3"

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
    MetricName='FlightsEngineRule3Metric',
    ChangeToken=change_token,
    Tags=[
        {
            'Key': 'Product',
            'Value': 'Flights'
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
                    'DataId': "13c89bd9-e2d4-4cf1-94ca-b88e28f876bf"
                }
            },
            #sql
            {
                'Action': 'INSERT',
                'Predicate': {
                    'Negated': True,
                    'Type': 'SqlInjectionMatch',
                    'DataId': "fca1970f-4948-4045-9417-77ae46908bef"
                }
            },
            #ccpa
            {
                'Action': 'INSERT',
                'Predicate': {
                    'Negated': True,
                    'Type': 'ByteMatch',
                    'DataId': "d9ba7eb6-1bbe-4eb3-8ab7-ffa89196f028"
                }
            },
            #xss
            {
                'Action': 'INSERT',
                'Predicate': {
                    'Negated': True,
                    'Type': 'XssMatch',
                    'DataId': "5bf10930-8717-4025-b800-55abde505ccb"
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