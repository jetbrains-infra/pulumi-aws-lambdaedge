import os
from setuptools import setup, find_packages

readme_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'README.md')


def get_content(path):
    with open(path, 'r') as f:
        return f.read()


setup(name='pulumi-aws-lambdaedge',
      version=os.environ.get('RELEASE_TAG', '0.0.0'),
      long_description=get_content(readme_path),
      long_description_content_type='text/markdown',
      description='Pulumi ComponentResource for create Lambda@Edge',
      url='https://github.com/jetbrains-infra/pulumi-aws-lambdaedge',
      author='Vadim Reyder',
      author_email='vadim.reyder@gmail.com',
      license='MIT',
      packages=find_packages(exclude=("tests",)),
      data_files=['requirements.txt'],
      install_requires=get_content('requirements.txt').split('\n'),
      zip_safe=False)
