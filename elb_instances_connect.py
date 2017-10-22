import boto3
import sys, os, string, threading
import paramiko
elb = boto3.client('elb')
ec2 = boto3.resource('ec2')

outlock = threading.Lock()

key_names = {'mumbai': '/home/ansible/.ssh/mumbai.pem', 'singapore': '/home/ansible/.ssh/singapore.pem'}
ssh_user = 'ubuntu'


load_balancer_names = ['travelui-beta']

def get_elb_descriptions():
	elb_describe = elb.describe_load_balancers(LoadBalancerNames=load_balancer_names)
	descriptions = elb_describe.get('LoadBalancerDescriptions')
	return descriptions[0]

def get_instances():
	descriptions = get_elb_descriptions()
	instances = []
	for instance in descriptions.get("Instances"):
		instances.append(instance.get("InstanceId"))
	instances = ec2.instances.filter(InstanceIds=instances)
	return instances

def get_instance_ips(instances):
	hosts = []
	for instance in instances:
		hosts.append({"host":instance.private_ip_address, "key_name": instance.key_name, "instance_id": instance.id})
        return hosts

def workon(instance):
	host = instance['host']
	key = key_names[instance['key_name']]
	
	paramiko.util.log_to_file("/tmp/elb_instances_connect.log")
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
	ssh_key = paramiko.RSAKey.from_private_key_file(key)


        command="pwd"

	try:
		ssh.connect(host, username = ssh_user, pkey = ssh_key)
		stdin, stdout, stderr = ssh.exec_command(command)
		print stdout.read(),
	except:
	   print("could not make a connection")
	
	

def main():
	instances = get_instances()
        hosts = get_instance_ips(instances)
	print(hosts)
	threads = []
	for h in hosts:
        	t = threading.Thread(target=workon, args=(h,))
	        t.start()
	        threads.append(t)
    	for t in threads:
        	t.join()
	

main()
