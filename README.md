# pulumi-aws-lambdaedge
Pulumi ComponentResource for create Lambda@Edge

# How to install
```bash
pip install --upgrade pip
pip install wheel
pip install pulumi-aws-lambdaedge
# or
pip install git+git://github.com/jetbrains-infra/pulumi-aws-lambdaedge@<tag or branch>
``` 

# How to use
```python
import pulumi
from pulumi_aws import Provider
from pulumi_aws_lambdaedge import LambdaEdge

us_provider = Provider('us-east-1-provider', region='us-east-1')

l = LambdaEdge('my-lambda',
               stack=pulumi.get_stack(),
               issue='sre-123',
               runtime='nodejs12.x',
               handler='index.handler',
               lambda_archive=pulumi.asset.FileArchive('./lambda'),
               memory_size_mb=128,
               timeout=5,
               opts=pulumi.ResourceOptions(provider=us_provider))

pulumi.export('lambda-arn', l.lambda_edge.arn)
```