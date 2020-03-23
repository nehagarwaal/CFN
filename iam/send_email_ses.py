import boto3
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import os
import sys

recipient_email = sys.argv[1]
password = sys.argv[2]

def get_ses_client():
    client = boto3.client("ses")
    return client

def send_raw_email_zip(ses_client):
    msg = MIMEMultipart('mixed')
    msg['Subject'] = 'IAM Access and Secret Key'
    msg['From'] = 'xyz@abc.com'
    msg['To'] = recipient_email

    attachment = "keys.zip"
    att = MIMEApplication(open(attachment, 'rb').read())
    att.add_header('Content-Disposition','attachment',filename=os.path.basename(attachment))
    msg.attach(att)
    ses_client.send_raw_email(
        Source=msg['From'],
        Destinations=[msg['To']],
        RawMessage={
            'Data':msg.as_string(),
        }
    )

def send_raw_email_pass(ses_client):
    msg = MIMEMultipart('mixed')
    msg['Subject'] = 'IAM Access and Secret Key Password'
    msg['From'] = 'xyz@abc.com'
    msg['To'] = recipient_email

    mail_content = password
    textpart = MIMEText(mail_content.encode("utf-8"), 'plain', "utf-8")
    msg_body = MIMEMultipart('alternative')
    msg_body.attach(textpart)
    msg.attach(msg_body)

    result = ses_client.send_raw_email(
        Source=msg['From'],
        Destinations=[msg['To']],
        RawMessage={
            'Data':msg.as_string(),
        }
    )
    print(result)

def main():
    ses_client = get_ses_client()
    send_raw_email_zip(ses_client)
    send_raw_email_pass(ses_client)

if __name__ == "__main__":
    main()
