#!/bin/bash

coverage run --branch --include='aws_lambda_decorators/*.py' -m unittest tests/test_*.py
coverage report -m --fail-under=100 --omit=tests/*,it/*,env*