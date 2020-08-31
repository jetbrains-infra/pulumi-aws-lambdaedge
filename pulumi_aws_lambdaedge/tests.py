import pulumi
import unittest

from typing import Optional, Tuple, List
from pulumi_aws_lambdaedge import LambdaEdge
from pulumi_aws import lambda_


class MyMocks(pulumi.runtime.Mocks):
    def new_resource(self,
                     type_: str,
                     name: str,
                     inputs: dict,
                     provider: Optional[str],
                     id_: Optional[str]) -> Tuple[str, dict]:
        if type_ == 'aws:lambda/function:Function':
            state = {
                'version': 1,
                'arn': 'arn',
            }
            return name + '_id', dict(inputs, **state)
        return name + '_id', inputs

    def call(self, token, args, provider):
        return {}


pulumi.runtime.set_mocks(MyMocks())


lambdaedge = LambdaEdge('test',
                        issue='sre-123',
                        stack='staging',
                        runtime='nodejs12.x',
                        lambda_archive=pulumi.FileAsset('./tests.py'),
                        handler='index.handler',
                        memory_size_mb=128,
                        timeout=5)


class TestingWithMocks(unittest.TestCase):
    @pulumi.runtime.test
    def test_check_tags(self):
        def check_tags(args: List[LambdaEdge]):
            le = args[0]

            self.assertEqual(le.tags.get('lambda-edge'), 'test-staging')
            self.assertEqual(le.tags.get('stack'), 'staging')
            self.assertEqual(le.tags.get('issue'), 'sre-123')

        return pulumi.Output.all(lambdaedge).apply(check_tags)

    @pulumi.runtime.test
    def test_check_options(self):
        lambdaedge.lambda_edge.timeout.apply(lambda x: self.assertEqual(x, 5.0))
        lambdaedge.lambda_edge.handler.apply(lambda x: self.assertEqual(x, 'index.handler'))
        lambdaedge.lambda_edge.runtime.apply(lambda x: self.assertEqual(x, 'nodejs12.x'))
        lambdaedge.lambda_edge.memory_size.apply(lambda x: self.assertEqual(x, 128))
        lambdaedge.lambda_edge.version.apply(lambda x: self.assertEqual(x, 1))


