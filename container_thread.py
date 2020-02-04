import boto3
import paramiko
import subprocess

def main():
    key = paramiko.RSAKey.from_private_key_file("C:/Flights/Python/container_thread/test1.pem")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cmd='''sudo su
        docker ps
        pwd'''

    # Connect/ssh to an instance
    try:
        client.connect(hostname="10.232.34.201", username="nagarwal", pkey=key)
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read())
        client.close()
        #break

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
