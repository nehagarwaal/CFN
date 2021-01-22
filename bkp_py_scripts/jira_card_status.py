from jira import JIRA
import sys

user = 'adnan@ejam.com'
token = 'DaYJwvN5pGArz7tDc0ghC299'
server = 'https://ejam.atlassian.net'

jira = JIRA(server, basic_auth = (user, token))
issue = jira.issue(sys.argv[1])
if str(issue.fields.status) == "PROD DEPLOY APPROVED":
    print("Approved")