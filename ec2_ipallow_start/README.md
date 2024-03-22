"Start EC2 Instance and Allow IP Python Script"

Before running this script, make sure to do the following changes:

In the "instance_start.py" script, replace <your_instance_id> with your actual instance ID.
In the "ipallow_script.py" script, replace <your_security_group_id> with your actual security group ID.

Also, remember to check the Lambda timeout and roles for required permissions before running this script. Below have a sample

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "logs:CreateLogGroup",
            "Resource": "arn:aws:logs:us-east-1:111111:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "ec2:ModifySecurityGroupRules",
                "ec2:GetSecurityGroupsForVpc",
                "ec2:*",
                "ec2:DescribeSecurityGroupRules",
                "ec2:AuthorizeSecurityGroupIngress"
            ],
            "Resource": "*"
        }
    ]
}