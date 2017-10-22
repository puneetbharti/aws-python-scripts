import boto3
elb = boto3.client('elb')
ec2 = boto3.resource('ec2')

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
	for instance in instances:
		print(instance.id, instance.instance_type, instance.private_ip_address)
        return instances

def main():
	instances = get_instances()
        instance_ips = get_instance_ips(instances)
	

main()
