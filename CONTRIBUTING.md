# Contributing

If you want to contribute to this project, fork this Github repo and clone the fork locally. Install the requirements in a python3 virtual environment, using pip/pip3:

`pip install -r requirements.txt`

Before submitting the PR, please ensure that:

- you run [__Bandit__](https://pypi.org/project/bandit/) for security checking and all checks are passing:

`bandit -r .`
 
- you run [__Prospector__](https://pypi.org/project/prospector/) for code analysis and all checks are passing:

`prospector`

- you run [__Coverage__](https://pypi.org/project/coverage/) and all unit tests are passing:

`coverage run --branch --source='.' -m unittest`

- you have 100% unit test coverage:

`coverage report -m --fail-under=100 --omit=*/__init__.py,tests/*,setup.py`