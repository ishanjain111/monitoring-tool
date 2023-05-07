import boto3
import csv

# Create an EC2 client
ec2 = boto3.client('ec2')
s3_client = boto3.client('s3')

# Retrieve information about all EC2 instances in all regions
instances = []
regions = ec2.describe_regions()
for region in regions['Regions']:
    region_name = region['RegionName']
    session = boto3.Session(region_name=region_name)
    ec2 = session.client('ec2')
    instances += ec2.describe_instances()['Reservations']

# Open a CSV file to write the instance information to
with open('ec2_instances_details.csv', mode='w', newline='') as csv_file:
    fieldnames = ['Instance ID', 'Instance Type', 'Image ID', 'VPC ID', 'State', 'Availability Region']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    # Loop through each instance and write its information to the CSV file
    for reservation in instances:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_type = instance['InstanceType']
            image_id = instance['ImageId']
            vpc_id = instance['VpcId']
            state = instance['State']['Name']
            availability_region = instance['Placement']['AvailabilityZone']

            writer.writerow({'Instance ID': instance_id, 'Instance Type': instance_type, 'Image ID': image_id, 'VPC ID': vpc_id, 'State': state, 'Availability Region': availability_region})

print('EC2 instance information has been saved to ec2_instances_details.csv')

upload_bucket_name = 'account-information'

response = None
try:
    response = s3_client.head_bucket(Bucket=upload_bucket_name)
except Exception as e:
    pass

if response is None:
    s3_client.create_bucket(Bucket=upload_bucket_name)
    print(f'Bucket {upload_bucket_name} created successfully.')
else:
    print(f'Bucket {upload_bucket_name} already exists.')


s3_client.upload_file('ec2_instances_details.csv', upload_bucket_name, 'ec2_instances_details.csv')
print(f'Files upload successful to the the bucket {upload_bucket_name}')

