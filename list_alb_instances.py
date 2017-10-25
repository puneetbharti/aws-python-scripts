import boto3
alb = boto3.client('elbv2')
ec2 = boto3.resource('ec2')

load_balancer_names = ['ext-travel']
load_balancer_arn = 'arn:aws:elasticloadbalancing:ap-southeast-1:359716425895:loadbalancer/app/ext-travel/4029a56a058089c9'
listener_arns = ['arn:aws:elasticloadbalancing:ap-southeast-1:359716425895:targetgroup/Bus/2df60c1df717d74c', 'arn:aws:elasticloadbalancing:ap-southeast-1:359716425895:targetgroup/bus-admin/130592484707d109']

def get_alb_descriptions():
	alb_describe = alb.describe_target_health(TargetGroupArn=listener_arns[1])
	descriptions = alb_describe.get('TargetHealthDescriptions')
	return descriptions

def get_instances():
	descriptions = get_alb_descriptions()
	instances = []
	for instance in descriptions:
		instances.append(instance.get("Target").get("Id"))
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
