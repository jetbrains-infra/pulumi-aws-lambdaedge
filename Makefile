venv:
	python3 -m venv venv

requirements:
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install wheel
	./venv/bin/pip install --upgrade -r requirements.txt

test:
	./venv/bin/python -m unittest pulumi_aws_lambdaedge.tests
