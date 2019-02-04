from setuptools import setup, find_packages

LONG_DESCRIPTION = open('README.md').read()

setup(name='aws_lambda_decorators',
      version='0.5',
      description='A set of python decorators to simplify aws python lambda development',
      long_description=LONG_DESCRIPTION,
      long_description_content_type="text/markdown",
      url='https://github.com/gridsmartercities/aws-lambda-decorators',
      author='Grid Developers',
      author_email='developers@gridsmartercities.com',
      license='MIT',
      classifiers=['Intended Audience :: Developers',
                   'Development Status :: 2 - Pre-Alpha',
                   'Programming Language :: Python :: 3',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Natural Language :: English'
                   ],
      keywords='aws lambda decorator',
      packages=find_packages(exclude=('tests',)),
      install_requires=[
          'boto3',
          'jwt'
      ],
      zip_safe=False
      )
