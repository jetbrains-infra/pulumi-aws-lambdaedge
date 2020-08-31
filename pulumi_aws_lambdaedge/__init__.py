import json

import pulumi
from pulumi_aws import iam
from pulumi_aws import lambda_


class LambdaTimeoutValidation(Exception):
    pass


LAMBDA_ROLE = {
    'Version': '2012-10-17',
    'Statement': [
        {
            'Effect': 'Allow',
            'Principal': {
                'Service': [
                    'lambda.amazonaws.com',
                    'edgelambda.amazonaws.com'
                ]
            },
            'Action': 'sts:AssumeRole'
        }
    ]
}

LAMBDA_CLOUDWATCH_POLICY = {
    'Version': '2012-10-17',
    'Statement': [
        {
            'Effect': 'Allow',
            'Action': [
                'logs:CreateLogGroup',
                'logs:CreateLogStream',
                'logs:PutLogEvents'
            ],
            'Resource': [
                'arn:aws:logs:*:*:*'
            ]
        }
    ]
}


class LambdaEdge(pulumi.ComponentResource):
    lambda_edge: lambda_.Function
    timeout: pulumi.Output[float]
    arn: pulumi.Output[str]

    def __init__(self,
                 name: str,
                 stack: str,
                 issue: str,
                 runtime: str,
                 handler: str,
                 lambda_archive: pulumi.Input[pulumi.Archive],
                 source_code_hash: str = None,
                 memory_size_mb: int = 128,
                 timeout: int = 1,
                 opts: pulumi.ResourceOptions = None):
        """
        Create Lambda for usage at CloudFront, please use us-east-1 provider in opts. Create Role and grant permissions
            for edgelambda.awsamazon.com
        :param name: Name of the component
        :param stack: Name of the stack, staging or prod for example, used for tags
        :param issue: Issue tracker id, used for tags
        :param runtime: Lambda runtime, supported runtimes: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/lambda-requirements-limits.html#lambda-requirements-lambda-function-configuration
        :param handler: Lambda handler
        :param lambda_archive: Archive with Lambda code
        :param source_code_hash: base64(sha256(lambda.zip))
        :param memory_size_mb: Lambda memory size in Mb, 128 Mb max for viewer request and response events
        :param timeout: Lambda timeout, max 30 seconds for origin request and response events and max 5 seconds for
            viewer request and response events, see details at https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/lambda-requirements-limits.html#lambda-requirements-see-limits
        :param opts: Standard Pulumi ResourceOptions
        """
        super().__init__('LambdaEdge', name, None, opts)
        self.name = name
        self.stack = stack
        self.issue = issue
        if timeout > 30:
            raise LambdaTimeoutValidation(
                'Maximum timeout for lambda@edge is 30 seconds for origin events and 5 seconds for viewer events')
        self.tags = {
            'lambda-edge': f'{self.name}-{self.stack}',
            'stack': self.stack,
            'issue': self.issue,
        }
        role = iam.Role(f'{name}-lambda-role',
                        path='/service-role/',
                        assume_role_policy=json.dumps(LAMBDA_ROLE),
                        tags=self.tags,
                        opts=pulumi.ResourceOptions(parent=self))

        iam.RolePolicy(f'{name}-lambda-policy',
                       role=role.id,
                       policy=json.dumps(LAMBDA_CLOUDWATCH_POLICY),
                       opts=pulumi.ResourceOptions(parent=self))

        lambda_edge = lambda_.Function(f'{name}-lambda-edge',
                                       description=f'Handler for processing index.html for stack: {stack}, '
                                                   f'issue: {issue}',
                                       runtime=runtime,
                                       handler=handler,
                                       code=lambda_archive,
                                       source_code_hash=source_code_hash,
                                       memory_size=memory_size_mb,
                                       timeout=timeout,
                                       publish=True,
                                       tags=self.tags,
                                       role=role.arn,
                                       opts=pulumi.ResourceOptions(parent=self))

        lambda_.Permission(f'{name}-lambda-edge-permission',
                           action='lambda:GetFunction',
                           function=lambda_edge,
                           principal='edgelambda.amazonaws.com',
                           opts=pulumi.ResourceOptions(parent=self))
        self.timeout = lambda_edge.timeout
        self.arn = lambda_edge.arn
        self.lambda_edge = lambda_edge
        self.register_outputs({
            'timeout': self.timeout,
            'arn': self.arn,
        })
