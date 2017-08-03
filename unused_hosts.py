import boto3
import sys, os, string, threading
import paramiko
from botocore.exceptions import ClientError


outlock = threading.Lock()

ec2 = boto3.resource('ec2')

key_names = {'mumbai': '/home/puneet/.ssh/mumbai.pem', 'singapore': '/home/puneet/.ssh/singapore.pem'}
ssh_user = 'ubuntu'
checkout_path = '/srv/code/'
uncommited_days = 3
git_format = "%H,%ad"
is_termination_enabled = True

valid_hosts = []   # where source is present and has made a commit in last 3 days
unused_hosts = []  # based on the commit id and last commit
unreachable_hosts = [] # unable to connect them with the given key and username
invalid_hosts = []  # source code directory not found 

instances = ec2.instances.filter(
    Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

def get_all_running_instances():
    instance_ips=[]
    for instance in instances:
	if instance.key_name in key_names:
		instance_ips.append({"host":instance.private_ip_address, "key_name": instance.key_name, "instance_id": instance.id})
    return instance_ips
	
def workon(instance):
    host = instance['host']
    key = key_names[instance['key_name']]
    instance_id = instance['instance_id']
    # git command to check last commit 
    cmd = 'cd %s && git log -1 --since=%d.days --format="%s"' % (checkout_path, uncommited_days, git_format)
 
    paramiko.util.log_to_file("filename.log")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_key = paramiko.RSAKey.from_private_key_file(key)
     
    try:
	    ssh.connect(host, username = ssh_user, pkey = ssh_key)
	    stdin, stdout, stderr = ssh.exec_command(cmd)
            output = stdout.read().split(",")
            error_output = stderr.read()
            
            # check if host is valid and has a code base 
	    if output[0]:
		valid_hosts.append({"host": host, "last_commit": output[0], "date": output[1], "instance_id": instance_id})
            elif output[0]=="":
		unused_hosts.append({"host": host, "msg": "source code not updated since last %d days" % uncommited_days, "instance_id": instance_id })
            
            if error_output:	    
	         invalid_hosts.append({"hosts": host, "msg": error_output, "instance_id": instance_id})

            ssh.close()
    except:
	   unreachable_hosts.append({"host": host, "msg": "host unreachable", "instance_id": instance_id})


def terminate_instance(instances):
    ids = []
    for instance in instances:
	ids.append(instance['instance_id'])
    print(ids)
    ec2.instances.filter(InstanceIds=ids).terminate()
    print("terminated")

def main():
    print(get_all_running_instances())	
    hosts = get_all_running_instances()
    threads = []
    for h in hosts:
        t = threading.Thread(target=workon, args=(h,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    print(valid_hosts)
    print(unreachable_hosts)
    print(invalid_hosts)
    print(unused_hosts)
    if is_termination_enabled:
	terminate_instance(unused_hosts)

main()
